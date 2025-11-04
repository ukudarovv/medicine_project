from rest_framework import serializers
from .models import (
    PatientPhone,
    PatientSocialNetwork,
    PatientContactPerson,
    PatientDisease,
    PatientDiagnosis,
    MedicalExamination,
    MedExamPastDisease,
    MedExamVaccination,
    MedExamLabTest,
    TreatmentPlan,
    TreatmentStage,
    TreatmentStageItem,
    TreatmentPlanTemplate
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


# ==================== Sprint 3: Medical Examination Serializers ====================


class MedExamPastDiseaseSerializer(serializers.ModelSerializer):
    icd_code_display = serializers.CharField(source='icd_code.code', read_only=True, allow_null=True)
    
    class Meta:
        model = MedExamPastDisease
        fields = ['id', 'examination', 'icd_code', 'icd_code_display', 'disease_name', 'year', 'note']
        read_only_fields = ['id']


class MedExamVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedExamVaccination
        fields = ['id', 'examination', 'vaccine_type', 'date', 'revaccination_date', 'serial_number', 'note']
        read_only_fields = ['id']


class MedExamLabTestSerializer(serializers.ModelSerializer):
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    
    class Meta:
        model = MedExamLabTest
        fields = ['id', 'examination', 'test_type', 'test_type_display', 'test_name', 'result', 'performed_date', 'file']
        read_only_fields = ['id']


class MedicalExaminationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    past_diseases = MedExamPastDiseaseSerializer(many=True, read_only=True)
    vaccinations = MedExamVaccinationSerializer(many=True, read_only=True)
    lab_tests = MedExamLabTestSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalExamination
        fields = [
            'id', 'patient', 'patient_name',
            'exam_type', 'exam_type_display', 'exam_date',
            'work_profile', 'conclusion', 'fit_for_work', 'restrictions',
            'next_exam_date', 'commission_members',
            'past_diseases', 'vaccinations', 'lab_tests',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


# ==================== Sprint 3: Treatment Plan Serializers ====================


class TreatmentStageItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True, allow_null=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='calculate_total')
    completion_percent = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TreatmentStageItem
        fields = [
            'id', 'stage', 'service', 'service_name', 'description',
            'qty_planned', 'qty_completed', 'unit_price', 'discount_percent',
            'total', 'completion_percent', 'tooth_number', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TreatmentStageSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = TreatmentStageItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='calculate_total_cost')
    
    class Meta:
        model = TreatmentStage
        fields = [
            'id', 'plan', 'order', 'title', 'description',
            'start_date', 'end_date', 'status', 'status_display',
            'items', 'total_cost',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TreatmentPlanSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    stages = TreatmentStageSerializer(many=True, read_only=True)
    calculated_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='calculate_total_cost')
    
    class Meta:
        model = TreatmentPlan
        fields = [
            'id', 'patient', 'patient_name',
            'title', 'description', 'total_cost', 'calculated_total', 'total_cost_frozen',
            'status', 'status_display', 'start_date', 'end_date',
            'stages',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TreatmentPlanTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = TreatmentPlanTemplate
        fields = [
            'id', 'organization', 'name', 'description', 'template_data',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

