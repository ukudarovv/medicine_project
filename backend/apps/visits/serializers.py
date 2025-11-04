from rest_framework import serializers
from .models import Visit, VisitService, VisitPrescription, VisitResource, VisitFile


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


class VisitFileSerializer(serializers.ModelSerializer):
    """Serializer for visit files"""
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = VisitFile
        fields = [
            'id', 'visit', 'file', 'file_type', 'file_type_display',
            'title', 'description', 'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class VisitSerializer(serializers.ModelSerializer):
    services_list = VisitServiceSerializer(many=True, read_only=True, source='services')
    prescriptions = VisitPrescriptionSerializer(many=True, read_only=True)
    resources = VisitResourceSerializer(many=True, read_only=True)
    files = VisitFileSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='appointment.patient.full_name', read_only=True)
    employee_name = serializers.CharField(source='appointment.employee.full_name', read_only=True)
    
    # Additional fields for frontend
    start_datetime = serializers.DateTimeField(source='appointment.start_datetime', read_only=True)
    branch_name = serializers.CharField(source='appointment.branch.name', read_only=True)
    
    # Service names for display
    services = serializers.SerializerMethodField()
    
    # Total amount
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Visit
        fields = [
            'id', 'appointment', 'patient_name', 'employee_name',
            'start_datetime', 'branch_name',
            'status', 'comment', 'is_patient_arrived', 'arrived_at',
            'diagnosis', 'treatment_plan',
            'services', 'services_list', 'prescriptions', 'resources',
            'total_amount',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Override to safely include Sprint 2 fields if they exist"""
        data = super().to_representation(instance)
        
        # Safely add Sprint 2 fields if they exist in DB
        if hasattr(instance, 'diary_structured'):
            data['diary_structured'] = instance.diary_structured
        if hasattr(instance, 'templates_used'):
            data['templates_used'] = instance.templates_used
        
        # Safely add files if relation exists
        if hasattr(instance, 'files'):
            try:
                data['files'] = VisitFileSerializer(instance.files.all(), many=True).data
            except:
                data['files'] = []
        
        return data
    
    def get_services(self, obj):
        """Return list of service names"""
        return [service.service.name for service in obj.services.all()]
    
    def get_total_amount(self, obj):
        """Calculate total amount from services"""
        total = sum(service.total_price for service in obj.services.all())
        return float(total)

