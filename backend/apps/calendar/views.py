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
    permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'patient', 'branch', 'room', 'status']
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.branch_id or self.request.query_params.get('branch')
        
        queryset = Appointment.objects.filter(
            branch__organization=user.organization
        )
        
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
        Check for appointment conflicts
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

