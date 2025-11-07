"""
Serializers for EHR (Electronic Health Records) API
"""
from rest_framework import serializers
from .models import EHRRecord
from apps.patients.models import Patient
from apps.org.models import Organization


class EHRRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for EHR records
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    author_name = serializers.SerializerMethodField(read_only=True)
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    
    class Meta:
        model = EHRRecord
        fields = [
            'id', 'patient', 'patient_name',
            'organization', 'organization_name',
            'author', 'author_name',
            'record_type', 'record_type_display',
            'title', 'payload',
            'content_type', 'object_id',
            'version', 'previous_version',
            'is_external', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'author', 'is_external',
            'created_at', 'updated_at', 'version', 'previous_version'
        ]
    
    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None
    
    def create(self, validated_data):
        # Set organization and author from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['organization'] = request.user.organization
            validated_data['author'] = request.user
            
            # Check if this is an external record (writing to another org's patient)
            patient = validated_data.get('patient')
            if patient and not patient.has_organization(request.user.organization):
                validated_data['is_external'] = True
        
        return super().create(validated_data)


class EHRRecordListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for list views
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    
    class Meta:
        model = EHRRecord
        fields = [
            'id', 'patient', 'patient_name',
            'organization', 'organization_name',
            'record_type', 'record_type_display',
            'title', 'is_external',
            'created_at'
        ]


class PatientEHRSummarySerializer(serializers.Serializer):
    """
    Summary of patient's EHR records across organizations
    """
    patient_id = serializers.IntegerField()
    patient_name = serializers.CharField()
    total_records = serializers.IntegerField()
    own_records = serializers.IntegerField()
    external_records = serializers.IntegerField()
    organizations = serializers.ListField(child=serializers.CharField())
    last_updated = serializers.DateTimeField()

