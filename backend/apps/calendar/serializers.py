from rest_framework import serializers
from .models import Availability, Appointment, AppointmentResource, Waitlist, Break
from apps.staff.serializers import EmployeeListSerializer
from apps.patients.serializers import PatientListSerializer
from datetime import datetime, timedelta


class AvailabilitySerializer(serializers.ModelSerializer):
    """
    Availability serializer
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = Availability
        fields = [
            'id', 'employee', 'employee_name', 'room', 'room_name',
            'weekday', 'weekday_display', 'time_from', 'time_to',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentResourceSerializer(serializers.ModelSerializer):
    """
    Appointment resource serializer
    """
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    
    class Meta:
        model = AppointmentResource
        fields = ['id', 'appointment', 'resource', 'resource_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment serializer
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_color = serializers.CharField(source='employee.color', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    color = serializers.CharField(read_only=True)
    allocated_resources = AppointmentResourceSerializer(many=True, read_only=True)
    
    # Visit information
    has_visit = serializers.SerializerMethodField()
    visit_id = serializers.SerializerMethodField()
    visit_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'branch', 'employee', 'employee_name', 'employee_color',
            'patient', 'patient_name', 'patient_phone', 'room', 'room_name',
            'start_datetime', 'end_datetime', 'duration_minutes',
            'status', 'status_display', 'is_primary', 'is_urgent',
            'note', 'cancellation_reason', 'color',
            'allocated_resources',
            'has_visit', 'visit_id', 'visit_status',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_has_visit(self, obj):
        """Check if appointment has associated visit"""
        return hasattr(obj, 'visit')
    
    def get_visit_id(self, obj):
        """Get visit ID if exists"""
        return obj.visit.id if hasattr(obj, 'visit') else None
    
    def get_visit_status(self, obj):
        """Get visit status if exists"""
        return obj.visit.status if hasattr(obj, 'visit') else None
    
    def validate(self, attrs):
        """
        Validate appointment times and conflicts
        """
        start = attrs.get('start_datetime')
        end = attrs.get('end_datetime')
        employee = attrs.get('employee')
        room = attrs.get('room')
        
        # Validate times
        if start and end and start >= end:
            raise serializers.ValidationError('Start time must be before end time')
        
        # Check employee conflicts
        if employee and start and end:
            instance_id = self.instance.id if self.instance else None
            overlapping = Appointment.objects.filter(
                employee=employee,
                start_datetime__lt=end,
                end_datetime__gt=start
            ).exclude(status__in=['canceled', 'no_show'])
            
            if instance_id:
                overlapping = overlapping.exclude(id=instance_id)
            
            if overlapping.exists():
                raise serializers.ValidationError(
                    'Employee has overlapping appointments at this time'
                )
        
        # Check room conflicts
        if room and start and end:
            instance_id = self.instance.id if self.instance else None
            overlapping = Appointment.objects.filter(
                room=room,
                start_datetime__lt=end,
                end_datetime__gt=start
            ).exclude(status__in=['canceled', 'no_show'])
            
            if instance_id:
                overlapping = overlapping.exclude(id=instance_id)
            
            if overlapping.exists():
                raise serializers.ValidationError(
                    'Room is already booked at this time'
                )
        
        return attrs


class AppointmentListSerializer(serializers.ModelSerializer):
    """
    Simplified appointment serializer for calendar views
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    color = serializers.CharField(read_only=True)
    
    # Visit information
    has_visit = serializers.SerializerMethodField()
    visit_id = serializers.SerializerMethodField()
    visit_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'employee', 'employee_name', 'patient', 'patient_name', 'patient_phone',
            'room', 'start_datetime', 'end_datetime',
            'status', 'is_primary', 'color',
            'has_visit', 'visit_id', 'visit_status'
        ]
    
    def get_has_visit(self, obj):
        """Check if appointment has associated visit"""
        return hasattr(obj, 'visit')
    
    def get_visit_id(self, obj):
        """Get visit ID if exists"""
        return obj.visit.id if hasattr(obj, 'visit') else None
    
    def get_visit_status(self, obj):
        """Get visit status if exists"""
        return obj.visit.status if hasattr(obj, 'visit') else None


class AppointmentMoveSerializer(serializers.Serializer):
    """
    Serializer for moving appointments (drag & drop)
    """
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField(required=False)
    employee_id = serializers.IntegerField(required=False)
    room_id = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        start = attrs.get('start_datetime')
        end = attrs.get('end_datetime')
        
        if end and start >= end:
            raise serializers.ValidationError('Start time must be before end time')
        
        return attrs


class WaitlistSerializer(serializers.ModelSerializer):
    """
    Waitlist serializer for patient waiting list (Sprint 2)
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True, allow_null=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    time_window_display = serializers.CharField(source='get_time_window_display', read_only=True)
    contacted_by_name = serializers.CharField(source='contacted_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Waitlist
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone',
            'service', 'service_name', 'employee', 'employee_name',
            'preferred_date', 'preferred_period_start', 'preferred_period_end',
            'time_window', 'time_window_display',
            'priority', 'comment', 'status', 'status_display',
            'contacted_at', 'contacted_by', 'contacted_by_name', 'contact_result',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BreakSerializer(serializers.ModelSerializer):
    """
    Break serializer for employee breaks/lunch/meetings
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    break_type_display = serializers.CharField(source='get_break_type_display', read_only=True)
    
    class Meta:
        model = Break
        fields = [
            'id', 'employee', 'employee_name', 'break_type', 'break_type_display',
            'date', 'start_time', 'end_time', 'note', 'is_recurring',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """
        Validate break times and conflicts
        """
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        employee = attrs.get('employee')
        date = attrs.get('date')
        
        # Validate times
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError('Start time must be before end time')
        
        # Check for overlapping breaks
        if employee and date and start_time and end_time:
            instance_id = self.instance.id if self.instance else None
            overlapping = Break.objects.filter(
                employee=employee,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if instance_id:
                overlapping = overlapping.exclude(id=instance_id)
            
            if overlapping.exists():
                raise serializers.ValidationError(
                    'Employee has overlapping breaks on this date'
                )
        
        return attrs
    
    def create(self, validated_data):
        """
        Create break(s) - if recurring, create for multiple days
        """
        is_recurring = validated_data.pop('is_recurring', False)
        
        # Create the main break
        break_obj = Break.objects.create(is_recurring=is_recurring, **validated_data)
        
        # If recurring, create for next 30 days
        if is_recurring:
            base_date = validated_data['date']
            employee = validated_data['employee']
            start_time = validated_data['start_time']
            end_time = validated_data['end_time']
            break_type = validated_data['break_type']
            note = validated_data.get('note', '')
            
            for i in range(1, 31):
                future_date = base_date + timedelta(days=i)
                # Check if break doesn't exist on this date
                if not Break.objects.filter(
                    employee=employee,
                    date=future_date,
                    start_time=start_time,
                    end_time=end_time
                ).exists():
                    Break.objects.create(
                        employee=employee,
                        break_type=break_type,
                        date=future_date,
                        start_time=start_time,
                        end_time=end_time,
                        note=note,
                        is_recurring=True
                    )
        
        return break_obj

