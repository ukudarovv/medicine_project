from rest_framework import serializers
from .models import Availability, Appointment, AppointmentResource
from apps.staff.serializers import EmployeeListSerializer
from apps.patients.serializers import PatientListSerializer


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
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'branch', 'employee', 'employee_name', 'employee_color',
            'patient', 'patient_name', 'patient_phone', 'room', 'room_name',
            'start_datetime', 'end_datetime', 'duration_minutes',
            'status', 'status_display', 'is_primary', 'is_urgent',
            'note', 'cancellation_reason', 'color',
            'allocated_resources',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
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
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'employee', 'employee_name', 'patient', 'patient_name', 'patient_phone',
            'room', 'start_datetime', 'end_datetime',
            'status', 'is_primary', 'color'
        ]


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

