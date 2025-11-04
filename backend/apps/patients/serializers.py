from rest_framework import serializers
from .models import (
    Patient, Representative, PatientFile,
    PatientPhone, PatientSocialNetwork, PatientContactPerson,
    PatientDisease, PatientDiagnosis, PatientDoseLoad
)


class RepresentativeSerializer(serializers.ModelSerializer):
    """
    Representative serializer
    """
    full_name = serializers.CharField(read_only=True)
    relation_display = serializers.CharField(source='get_relation_display', read_only=True)
    
    class Meta:
        model = Representative
        fields = [
            'id', 'patient', 'first_name', 'last_name', 'middle_name',
            'full_name', 'relation', 'relation_display', 'phone', 'email',
            'documents', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientFileSerializer(serializers.ModelSerializer):
    """
    Patient file serializer
    """
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = PatientFile
        fields = [
            'id', 'patient', 'file_type', 'file_type_display', 'title',
            'file', 'description', 'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPhone
        fields = ['id', 'patient', 'phone', 'type', 'note', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientSocialNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientSocialNetwork
        fields = ['id', 'patient', 'network', 'username', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientContactPersonSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientContactPerson
        fields = ['id', 'patient', 'first_name', 'last_name', 'full_name', 'relation', 'phone', 'email', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"


class PatientDiseaseSerializer(serializers.ModelSerializer):
    icd_code_display = serializers.CharField(source='icd_code.code', read_only=True, allow_null=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = PatientDisease
        fields = [
            'id', 'patient', 'start_date', 'end_date', 'diagnosis',
            'icd_code', 'icd_code_display', 'doctor', 'doctor_name', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientDiagnosisSerializer(serializers.ModelSerializer):
    icd_code_display = serializers.CharField(source='icd_code.code', read_only=True, allow_null=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True, allow_null=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = PatientDiagnosis
        fields = [
            'id', 'patient', 'date', 'diagnosis', 'icd_code', 'icd_code_display',
            'type', 'type_display', 'doctor', 'doctor_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientDoseLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoseLoad
        fields = ['id', 'patient', 'date', 'study_type', 'dose', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientSerializer(serializers.ModelSerializer):
    """
    Patient serializer
    """
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    sex_display = serializers.CharField(source='get_sex_display', read_only=True)
    representatives = RepresentativeSerializer(many=True, read_only=True)
    files = PatientFileSerializer(many=True, read_only=True)
    additional_phones = PatientPhoneSerializer(many=True, read_only=True)
    social_networks = PatientSocialNetworkSerializer(many=True, read_only=True)
    contact_persons = PatientContactPersonSerializer(many=True, read_only=True)
    diseases = PatientDiseaseSerializer(many=True, read_only=True)
    diagnoses = PatientDiagnosisSerializer(many=True, read_only=True)
    dose_loads = PatientDoseLoadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'organization', 'first_name', 'last_name', 'middle_name',
            'full_name', 'birth_date', 'age', 'sex', 'sex_display',
            'phone', 'email', 'address', 'iin', 'documents',
            'consents', 'tags', 'is_marketing_opt_in', 'balance', 'discount_percent',
            'notes', 'allergies', 'medical_history',
            'representatives', 'files', 'additional_phones', 'social_networks',
            'contact_persons', 'diseases', 'diagnoses', 'dose_loads',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_phone(self, value):
        """
        Validate that phone is unique within organization
        """
        organization = self.context['request'].user.organization
        
        # Normalize phone (remove non-digits)
        import re
        normalized = re.sub(r'\D', '', value)
        
        # Check for duplicates
        query = Patient.objects.filter(
            organization=organization,
            phone__iregex=f'[^0-9]*{normalized}[^0-9]*'
        )
        
        # Exclude current patient in update
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            existing = query.first()
            raise serializers.ValidationError(
                f'Пациент с таким телефоном уже существует: {existing.full_name}'
            )
        
        return value
    
    def validate_iin(self, value):
        """
        Validate that IIN is unique within organization (if provided)
        """
        if not value:
            return value
        
        organization = self.context['request'].user.organization
        
        # Check for duplicates
        query = Patient.objects.filter(
            organization=organization,
            iin=value
        )
        
        # Exclude current patient in update
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            existing = query.first()
            raise serializers.ValidationError(
                f'Пациент с таким ИИН уже существует: {existing.full_name}'
            )
        
        return value


class PatientListSerializer(serializers.ModelSerializer):
    """
    Simplified patient serializer for lists
    """
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'birth_date', 'age', 'phone', 'balance', 'is_active'
        ]


class PatientSearchSerializer(serializers.Serializer):
    """
    Serializer for patient search by phone/IIN
    """
    phone = serializers.CharField(required=False)
    iin = serializers.CharField(required=False)
    
    def validate(self, attrs):
        if not attrs.get('phone') and not attrs.get('iin'):
            raise serializers.ValidationError('Укажите телефон или ИИН')
        return attrs
