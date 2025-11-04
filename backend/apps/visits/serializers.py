from rest_framework import serializers
from .models import Visit, VisitService, VisitPrescription, VisitResource


class VisitServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = VisitService
        fields = [
            'id', 'visit', 'service', 'service_name', 'icd',
            'qty', 'duration', 'price', 'discount_percent', 'discount_amount',
            'tooth_number', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VisitPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitPrescription
        fields = ['id', 'visit', 'medication', 'dosage', 'frequency', 'duration_days', 'instructions', 'created_at']
        read_only_fields = ['id', 'created_at']


class VisitResourceSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    
    class Meta:
        model = VisitResource
        fields = ['id', 'visit', 'resource', 'resource_name', 'used_time', 'created_at']
        read_only_fields = ['id', 'created_at']


class VisitSerializer(serializers.ModelSerializer):
    services = VisitServiceSerializer(many=True, read_only=True)
    prescriptions = VisitPrescriptionSerializer(many=True, read_only=True)
    resources = VisitResourceSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='appointment.patient.full_name', read_only=True)
    employee_name = serializers.CharField(source='appointment.employee.full_name', read_only=True)
    
    class Meta:
        model = Visit
        fields = [
            'id', 'appointment', 'patient_name', 'employee_name',
            'status', 'comment', 'is_patient_arrived', 'arrived_at',
            'diagnosis', 'treatment_plan',
            'services', 'prescriptions', 'resources',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

