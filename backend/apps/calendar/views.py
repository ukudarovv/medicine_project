from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.core.permissions import IsBranchMember, IsBranchAdmin
from .models import Availability, Appointment, AppointmentResource
from .serializers import (
    AvailabilitySerializer,
    AppointmentSerializer,
    AppointmentListSerializer,
    AppointmentMoveSerializer,
    AppointmentResourceSerializer
)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """
    Availability CRUD
    """
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'weekday', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        employee_id = self.request.query_params.get('employee')
        
        queryset = Availability.objects.filter(
            employee__organization=user.organization
        )
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset.select_related('employee', 'room')


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Appointment CRUD with WebSocket notifications
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # Temporarily disabled for development
    # permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'patient', 'branch', 'room', 'status']
    
    def get_queryset(self):
        # TODO: Enable organization filtering in production
        # user = self.request.user
        branch_id = self.request.query_params.get('branch')
        
        queryset = Appointment.objects.all()
        
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            queryset = queryset.filter(start_datetime__gte=date_from)
        
        if date_to:
            date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            queryset = queryset.filter(start_datetime__lte=date_to)
        
        # Filter by today
        if self.request.query_params.get('today'):
            today = timezone.now().date()
            queryset = queryset.filter(
                start_datetime__date=today
            )
        
        return queryset.select_related(
            'employee', 'patient', 'room', 'branch'
        ).prefetch_related('allocated_resources')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AppointmentListSerializer
        return AppointmentSerializer
    
    def perform_create(self, serializer):
        appointment = serializer.save(created_by=self.request.user)
        
        # Send WebSocket notification
        self.send_websocket_event(appointment, 'appointment_created')
    
    def perform_update(self, serializer):
        appointment = serializer.save()
        
        # Send WebSocket notification
        self.send_websocket_event(appointment, 'appointment_updated')
    
    def perform_destroy(self, instance):
        branch_id = instance.branch_id
        appointment_id = instance.id
        instance.delete()
        
        # Send WebSocket notification
        self.send_websocket_event_raw(branch_id, {
            'type': 'appointment_deleted',
            'appointment_id': appointment_id
        })
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """
        Move appointment (drag & drop)
        """
        appointment = self.get_object()
        serializer = AppointmentMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Calculate duration if end_datetime not provided
        if not serializer.validated_data.get('end_datetime'):
            duration = appointment.end_datetime - appointment.start_datetime
            serializer.validated_data['end_datetime'] = (
                serializer.validated_data['start_datetime'] + duration
            )
        
        # Update appointment
        appointment.start_datetime = serializer.validated_data['start_datetime']
        appointment.end_datetime = serializer.validated_data['end_datetime']
        
        if serializer.validated_data.get('employee_id'):
            appointment.employee_id = serializer.validated_data['employee_id']
        
        if serializer.validated_data.get('room_id'):
            appointment.room_id = serializer.validated_data['room_id']
        
        # Validate conflicts
        appointment.clean()
        appointment.save()
        
        # Send WebSocket notification
        self.send_websocket_event(appointment, 'appointment_moved')
        
        return Response(AppointmentSerializer(appointment).data)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        Change appointment status
        """
        appointment = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status or new_status not in dict(Appointment.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = new_status
        
        # Set cancellation reason if canceled
        if new_status == 'canceled':
            appointment.cancellation_reason = request.data.get('cancellation_reason', '')
        
        appointment.save()
        
        # Send WebSocket notification
        self.send_websocket_event(appointment, 'appointment_status_changed')
        
        return Response(AppointmentSerializer(appointment).data)
    
    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        """
        Check for appointment conflicts (with HR integration)
        """
        employee_id = request.query_params.get('employee')
        room_id = request.query_params.get('room')
        start_datetime = request.query_params.get('start_datetime')
        end_datetime = request.query_params.get('end_datetime')
        exclude_id = request.query_params.get('exclude_id')
        
        if not (start_datetime and end_datetime):
            return Response(
                {'error': 'start_datetime and end_datetime are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
        
        conflicts = []
        
        # Check employee conflicts
        if employee_id:
            from apps.staff.models import Employee
            
            # Check if employee is visible in schedule
            try:
                employee = Employee.objects.get(id=employee_id)
                if not employee.show_in_schedule:
                    conflicts.append({
                        'type': 'employee',
                        'message': 'Employee is not available for appointments'
                    })
            except Employee.DoesNotExist:
                pass
            
            # Check overlapping appointments
            employee_conflicts = Appointment.objects.filter(
                employee_id=employee_id,
                start_datetime__lt=end,
                end_datetime__gt=start
            ).exclude(status__in=['canceled', 'no_show'])
            
            if exclude_id:
                employee_conflicts = employee_conflicts.exclude(id=exclude_id)
            
            if employee_conflicts.exists():
                conflicts.append({
                    'type': 'employee',
                    'message': 'Employee has overlapping appointments'
                })
            
            # Check minimum gap between visits
            if hasattr(employee, 'min_gap_between_visits_minutes') and employee.min_gap_between_visits_minutes:
                gap_minutes = employee.min_gap_between_visits_minutes
                gap_delta = timedelta(minutes=gap_minutes)
                
                nearby_appointments = Appointment.objects.filter(
                    employee_id=employee_id,
                    start_datetime__lt=start + gap_delta,
                    end_datetime__gt=start - gap_delta
                ).exclude(status__in=['canceled', 'no_show'])
                
                if exclude_id:
                    nearby_appointments = nearby_appointments.exclude(id=exclude_id)
                
                if nearby_appointments.exists():
                    conflicts.append({
                        'type': 'employee_gap',
                        'message': f'Minimum gap of {gap_minutes} minutes between visits not met'
                    })
        
        # Check room conflicts
        if room_id:
            room_conflicts = Appointment.objects.filter(
                room_id=room_id,
                start_datetime__lt=end,
                end_datetime__gt=start
            ).exclude(status__in=['canceled', 'no_show'])
            
            if exclude_id:
                room_conflicts = room_conflicts.exclude(id=exclude_id)
            
            if room_conflicts.exists():
                conflicts.append({
                    'type': 'room',
                    'message': 'Room is already booked'
                })
        
        return Response({
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        })
    
    @action(detail=False, methods=['get'])
    def available_employees(self, request):
        """
        Get list of employees available for scheduling
        """
        from apps.staff.models import Employee
        
        branch_id = request.query_params.get('branch')
        position_id = request.query_params.get('position')
        
        queryset = Employee.objects.filter(
            organization=request.user.organization,
            show_in_schedule=True,
            employment_status='active',
            is_active=True
        )
        
        if branch_id:
            queryset = queryset.filter(branch_assignments__branch_id=branch_id)
        
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        
        employees = []
        for emp in queryset:
            employees.append({
                'id': emp.id,
                'full_name': emp.full_name,
                'position': emp.position.name if emp.position else emp.position_legacy,
                'color': emp.calendar_color or emp.color,
                'online_slot_step_minutes': emp.online_slot_step_minutes,
                'min_gap_between_visits_minutes': emp.min_gap_between_visits_minutes
            })
        
        return Response(employees)
    
    @action(detail=False, methods=['get'])
    def online_booking_slots(self, request):
        """
        Get available slots for online booking (considering employee settings)
        """
        from apps.staff.models import Employee
        
        employee_id = request.query_params.get('employee')
        date = request.query_params.get('date')
        
        if not (employee_id and date):
            return Response(
                {'error': 'employee and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if employee is available for online booking
        if not employee.show_in_schedule or employee.employment_status != 'active':
            return Response({'slots': []})
        
        # Get slot step (individual or default)
        slot_step_minutes = employee.online_slot_step_minutes or 30  # default 30 min
        
        # Parse date
        target_date = datetime.fromisoformat(date).date()
        weekday = target_date.weekday()
        
        # Get employee availability for this weekday
        availabilities = Availability.objects.filter(
            employee=employee,
            weekday=weekday,
            is_active=True
        )
        
        if not availabilities.exists():
            return Response({'slots': []})
        
        # Generate time slots
        slots = []
        for availability in availabilities:
            current_time = datetime.combine(target_date, availability.time_from)
            end_time = datetime.combine(target_date, availability.time_to)
            
            while current_time < end_time:
                slot_end = current_time + timedelta(minutes=slot_step_minutes)
                
                # Check if slot is not already booked
                conflicts = Appointment.objects.filter(
                    employee=employee,
                    start_datetime__lt=timezone.make_aware(slot_end),
                    end_datetime__gt=timezone.make_aware(current_time)
                ).exclude(status__in=['canceled', 'no_show']).exists()
                
                if not conflicts:
                    slots.append({
                        'start': current_time.isoformat(),
                        'end': slot_end.isoformat(),
                        'available': True
                    })
                
                current_time = slot_end
        
        return Response({'slots': slots})
    
    def send_websocket_event(self, appointment, event_type):
        """
        Send WebSocket event for appointment changes
        """
        channel_layer = get_channel_layer()
        group_name = f'calendar_branch_{appointment.branch_id}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'appointment_event',
                'data': {
                    'type': event_type,
                    'appointment': AppointmentListSerializer(appointment).data
                }
            }
        )
    
    def send_websocket_event_raw(self, branch_id, data):
        """
        Send raw WebSocket event
        """
        channel_layer = get_channel_layer()
        group_name = f'calendar_branch_{branch_id}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'appointment_event',
                'data': data
            }
        )


class AppointmentResourceViewSet(viewsets.ModelViewSet):
    """
    Appointment resource allocation CRUD
    """
    queryset = AppointmentResource.objects.all()
    serializer_class = AppointmentResourceSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        appointment_id = self.request.query_params.get('appointment')
        
        queryset = AppointmentResource.objects.filter(
            appointment__branch__organization=user.organization
        )
        
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)
        
        return queryset.select_related('appointment', 'resource')

