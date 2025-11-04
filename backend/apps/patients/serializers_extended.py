from rest_framework import serializers
from .models import (
    PatientPhone,
    PatientSocialNetwork,
    PatientContactPerson,
    PatientDisease,
    PatientDiagnosis
)


class PatientPhoneSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = PatientPhone
        fields = ['id', 'patient', 'phone', 'type', 'type_display', 'note', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientSocialNetworkSerializer(serializers.ModelSerializer):
    network_display = serializers.CharField(source='get_network_display', read_only=True)
    
    class Meta:
        model = PatientSocialNetwork
        fields = ['id', 'patient', 'network', 'network_display', 'username', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientContactPersonSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientContactPerson
        fields = [
            'id', 'patient', 'first_name', 'last_name', 'full_name',
            'relation', 'phone', 'email', 'note', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"


class PatientDiseaseSerializer(serializers.ModelSerializer):
    icd_code_display = serializers.CharField(source='icd_code.code', read_only=True)
    icd_name = serializers.CharField(source='icd_code.name_ru', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = PatientDisease
        fields = [
            'id', 'patient', 'start_date', 'end_date', 'diagnosis',
            'icd_code', 'icd_code_display', 'icd_name',
            'doctor', 'doctor_name', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientDiagnosisSerializer(serializers.ModelSerializer):
    icd_code_display = serializers.CharField(source='icd_code.code', read_only=True)
    icd_name = serializers.CharField(source='icd_code.name_ru', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    doctor_position = serializers.CharField(source='doctor.position', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = PatientDiagnosis
        fields = [
            'id', 'patient', 'date', 'diagnosis',
            'icd_code', 'icd_code_display', 'icd_name',
            'type', 'type_display',
            'doctor', 'doctor_name', 'doctor_position', 'doctor_specialization',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

