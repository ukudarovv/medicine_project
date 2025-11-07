from rest_framework import serializers
from .models import (
    Patient, Representative, PatientFile,
    PatientPhone, PatientSocialNetwork, PatientContactPerson,
    PatientDisease, PatientDiagnosis, PatientDoseLoad, ConsentHistory
)
from .validators import validate_iin


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


# ============================================================================
# TEMPORARILY DISABLED - Uncomment after migrations
# ============================================================================
# class ConsentHistorySerializer(serializers.ModelSerializer):
#     """
#     Consent history serializer for KZ compliance
#     """
#     consent_type_display = serializers.CharField(source='get_consent_type_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     accepted_by_name = serializers.CharField(source='accepted_by.get_full_name', read_only=True, allow_null=True)
#     
#     class Meta:
#         model = ConsentHistory
#         fields = [
#             'id', 'patient', 'consent_type', 'consent_type_display',
#             'status', 'status_display', 'ip_address', 'user_agent',
#             'accepted_by', 'accepted_by_name', 'created_at'
#         ]
#         read_only_fields = ['id', 'created_at']
# ============================================================================


class PatientSerializer(serializers.ModelSerializer):
    """
    Patient serializer
    """
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    sex_display = serializers.CharField(source='get_sex_display', read_only=True)
    osms_status_display = serializers.SerializerMethodField()
    osms_category_display = serializers.SerializerMethodField()
    representatives = RepresentativeSerializer(many=True, read_only=True)
    files = PatientFileSerializer(many=True, read_only=True)
    additional_phones = PatientPhoneSerializer(many=True, read_only=True)
    social_networks = PatientSocialNetworkSerializer(many=True, read_only=True)
    contact_persons = PatientContactPersonSerializer(many=True, read_only=True)
    diseases = PatientDiseaseSerializer(many=True, read_only=True)
    diagnoses = PatientDiagnosisSerializer(many=True, read_only=True)
    dose_loads = PatientDoseLoadSerializer(many=True, read_only=True)
    # consent_history = ConsentHistorySerializer(many=True, read_only=True)  # Disabled until migrations
    
    class Meta:
        model = Patient
        fields = [
            'id', 'organizations', 'first_name', 'last_name', 'middle_name',
            'full_name', 'birth_date', 'age', 'sex', 'sex_display',
            'phone', 'email', 'address', 'iin', 'documents',
            'osms_status_display', 'osms_category_display',
            'consents', 'tags', 'is_marketing_opt_in', 'balance', 'discount_percent',
            'notes', 'allergies', 'medical_history',
            'representatives', 'files', 'additional_phones', 'social_networks',
            'contact_persons', 'diseases', 'diagnoses', 'dose_loads',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Override to safely include KZ fields if they exist"""
        data = super().to_representation(instance)
        
        # Safely add KZ fields if they exist in DB
        if hasattr(instance, 'iin_verified'):
            data['iin_verified'] = instance.iin_verified
        if hasattr(instance, 'iin_verified_at'):
            data['iin_verified_at'] = instance.iin_verified_at
        if hasattr(instance, 'kato_address'):
            data['kato_address'] = instance.kato_address
        if hasattr(instance, 'osms_status'):
            data['osms_status'] = instance.osms_status
            data['osms_status_display'] = self.get_osms_status_display(instance)
        if hasattr(instance, 'osms_category'):
            data['osms_category'] = instance.osms_category
            data['osms_category_display'] = self.get_osms_category_display(instance)
        if hasattr(instance, 'osms_verified_at'):
            data['osms_verified_at'] = instance.osms_verified_at
        
        # Safely add consent_history if exists
        if hasattr(instance, 'consent_history'):
            try:
                # Temporarily disabled - uncomment after migrations
                # data['consent_history'] = ConsentHistorySerializer(instance.consent_history.all(), many=True).data
                data['consent_history'] = []
            except:
                data['consent_history'] = []
        
        return data
    
    def validate_phone(self, value):
        """
        Validate that phone is unique within organization
        """
        # Allow empty phone during development
        if not value:
            return value
            
        try:
            organization = self.context['request'].user.organization
        except (KeyError, AttributeError):
            # If no user context (e.g., testing), skip validation
            return value
        
        # Normalize phone (remove non-digits)
        import re
        normalized = re.sub(r'\D', '', value)
        
        # Skip validation if phone is too short
        if len(normalized) < 10:
            return value
        
        # Check for duplicates within the same organization
        try:
            query = Patient.objects.filter(
                organizations=organization,
                phone__iregex=f'[^0-9]*{normalized}[^0-9]*'
            )
            
            # Exclude current patient in update
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                existing = query.first()
                raise serializers.ValidationError(
                    f'Пациент с таким телефоном уже существует в вашей организации: {existing.full_name}'
                )
        except Exception as e:
            # Log error but don't fail validation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Phone validation error: {e}')
        
        return value
    
    def get_osms_status_display(self, obj):
        """Safe getter for OSMS status display"""
        try:
            return obj.get_osms_status_display() if hasattr(obj, 'osms_status') and obj.osms_status else None
        except AttributeError:
            return None
    
    def get_osms_category_display(self, obj):
        """Safe getter for OSMS category display"""
        try:
            return obj.get_osms_category_display() if hasattr(obj, 'osms_category') and obj.osms_category else None
        except AttributeError:
            return None
    
    def validate_iin(self, value):
        """
        Validate IIN format and uniqueness within organization
        """
        if not value:
            return value
        
        # Validate IIN format using KZ validator (only if IIN is provided)
        try:
            validation_result = validate_iin(value)
            if not validation_result['valid']:
                # Warning instead of error for better UX
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'IIN validation failed: {validation_result.get("error")}')
                # Still allow saving with invalid IIN in development
                # raise serializers.ValidationError(validation_result['error'])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'IIN validation error: {e}')
        
        try:
            organization = self.context['request'].user.organization
            
            # Check for duplicates within the same organization
            query = Patient.objects.filter(
                organizations=organization,
                iin=value
            )
            
            # Exclude current patient in update
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                existing = query.first()
                raise serializers.ValidationError(
                    f'Пациент с таким ИИН уже существует в вашей организации: {existing.full_name}'
                )
        except (KeyError, AttributeError):
            # If no user context, skip validation
            pass
        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Log other errors but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'IIN uniqueness check error: {e}')
        
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
