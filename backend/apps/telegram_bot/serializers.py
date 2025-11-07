"""
Serializers for Telegram Bot API
"""
from rest_framework import serializers
from apps.patients.models import Patient
from apps.org.models import Branch
from apps.services.models import Service
from apps.staff.models import Employee
from apps.calendar.models import Appointment, Availability
from .models import (
    PatientTelegramLink,
    BotBroadcast,
    BotDocument,
    BotAudit,
    BotFeedback,
    SupportTicket
)
from apps.patients.validators import validate_iin
from datetime import datetime, timedelta


class PatientTelegramLinkSerializer(serializers.ModelSerializer):
    """Serializer for PatientTelegramLink"""
    patient_full_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    
    class Meta:
        model = PatientTelegramLink
        fields = [
            'id', 'patient', 'telegram_user_id', 'telegram_username',
            'language', 'consents_json', 'is_active',
            'last_interaction_at', 'created_at',
            'patient_full_name', 'patient_phone'
        ]
        read_only_fields = ['id', 'created_at', 'last_interaction_at']


class PatientUpsertSerializer(serializers.Serializer):
    """Serializer for creating/updating patient via bot"""
    # Telegram data
    telegram_user_id = serializers.IntegerField(required=True)
    telegram_username = serializers.CharField(required=False, allow_blank=True)
    language = serializers.ChoiceField(choices=['ru', 'kk'], default='ru')
    
    # Patient data
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20)
    birth_date = serializers.DateField()
    sex = serializers.ChoiceField(choices=['M', 'F'])
    iin = serializers.CharField(max_length=12, required=False, allow_blank=True)
    
    # Consents
    consents = serializers.JSONField(required=False, default=dict)
    
    # Organization
    organization_id = serializers.IntegerField(required=True)
    
    def validate_iin(self, value):
        """Validate IIN using existing validator"""
        if value:
            result = validate_iin(value)
            if not result['valid']:
                raise serializers.ValidationError('Invalid IIN')
        return value


class BranchSerializer(serializers.ModelSerializer):
    """Simple branch serializer for bot"""
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone']


class ServiceSerializer(serializers.ModelSerializer):
    """Simple service serializer for bot"""
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'duration_minutes']


class DoctorSerializer(serializers.ModelSerializer):
    """Simple employee (doctor) serializer for bot"""
    specialty = serializers.CharField(source='position', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'specialty', 'photo']


class TimeSlotSerializer(serializers.Serializer):
    """Time slot for appointments"""
    time = serializers.TimeField()
    available = serializers.BooleanField()


class AppointmentCreateSerializer(serializers.Serializer):
    """Create appointment via bot"""
    telegram_user_id = serializers.IntegerField(required=True)
    employee_id = serializers.IntegerField(required=True)
    service_id = serializers.IntegerField(required=True)
    branch_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    time = serializers.TimeField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class AppointmentSerializer(serializers.ModelSerializer):
    """Appointment serializer for bot"""
    doctor_name = serializers.CharField(source='employee.full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_address = serializers.CharField(source='branch.address', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'date', 'time_from', 'time_to',
            'doctor_name', 'service_name', 'branch_name', 'branch_address',
            'status', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BotDocumentSerializer(serializers.ModelSerializer):
    """Bot document serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = BotDocument
        fields = [
            'id', 'patient', 'patient_name', 'document_type',
            'title', 'language', 'file_path', 'expires_at',
            'is_expired', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_expired']


class BotFeedbackSerializer(serializers.ModelSerializer):
    """Bot feedback serializer"""
    class Meta:
        model = BotFeedback
        fields = [
            'id', 'appointment', 'patient_telegram_link',
            'score', 'comment', 'is_low_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_low_score']


class BotFeedbackCreateSerializer(serializers.Serializer):
    """Create feedback via bot"""
    telegram_user_id = serializers.IntegerField(required=True)
    appointment_id = serializers.IntegerField(required=True)
    score = serializers.IntegerField(min_value=0, max_value=10)
    comment = serializers.CharField(required=False, allow_blank=True)


class SupportTicketSerializer(serializers.ModelSerializer):
    """Support ticket serializer"""
    patient_name = serializers.CharField(source='patient_telegram_link.patient.full_name', read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'patient_telegram_link', 'patient_name',
            'subject', 'message', 'status',
            'assigned_to', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at']


class SupportTicketCreateSerializer(serializers.Serializer):
    """Create support ticket via bot"""
    telegram_user_id = serializers.IntegerField(required=True)
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(style={'base_template': 'textarea.html'})


class BotBroadcastSerializer(serializers.ModelSerializer):
    """Bot broadcast serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = BotBroadcast
        fields = [
            'id', 'organization', 'title', 'segment_filters_json',
            'text_ru', 'text_kk', 'status', 'scheduled_at',
            'total_recipients', 'sent_count', 'delivered_count',
            'failed_count', 'clicked_count',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'total_recipients', 'sent_count',
            'delivered_count', 'failed_count', 'clicked_count'
        ]

