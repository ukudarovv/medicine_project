from rest_framework import serializers
from django.utils import timezone
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
    # files field is added in to_representation() method to handle Sprint 2 migration
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


class VisitNoteSerializer(serializers.Serializer):
    """
    Serializer for saving dictation/visit notes from desktop app
    """
    visit_id = serializers.IntegerField(required=True)
    raw_transcript = serializers.CharField(required=True, allow_blank=False)
    structured_data = serializers.JSONField(required=False, default=dict)
    language = serializers.ChoiceField(choices=['ru', 'kk'], default='ru')
    audio_duration = serializers.IntegerField(required=False, allow_null=True, help_text='Duration in seconds')
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_visit_id(self, value):
        """Validate visit exists and user has access"""
        try:
            visit = Visit.objects.get(id=value)
        except Visit.DoesNotExist:
            raise serializers.ValidationError('Visit not found')
        
        # Store visit for later use
        self.context['visit'] = visit
        return value
    
    def validate(self, attrs):
        """Additional validation"""
        visit = self.context.get('visit')
        user = self.context.get('request').user if 'request' in self.context else None
        
        if not visit:
            raise serializers.ValidationError('Visit not found')
        
        # Check if user has write access (either own org or active grant)
        if user:
            # TEMPORARILY DISABLED - consent app not in container
            # from apps.consent.models import AccessGrant
            
            # Check if same org
            is_own_org = visit.appointment.patient.has_organization(user.organization)
            
            # TEMPORARILY DISABLED - consent app not in container
            # # Check if has active grant with write_records scope
            # has_grant = AccessGrant.objects.filter(
            #     patient=visit.appointment.patient,
            #     grantee_org=user.organization,
            #     scopes__contains=['write_records'],
            #     valid_from__lte=timezone.now(),
            #     valid_to__gte=timezone.now(),
            #     revoked_at__isnull=True
            # ).exists()
            has_grant = False  # Temporarily set to False
            
            if not (is_own_org or has_grant):
                raise serializers.ValidationError('No permission to write to this visit')
        
        return attrs
    
    def save(self):
        """Save visit note and create EHR record"""
        visit = self.context['visit']
        user = self.context.get('request').user if 'request' in self.context else None
        
        # Update visit with transcript
        structured = self.validated_data.get('structured_data', {})
        
        # Update diary_structured with new data
        if hasattr(visit, 'diary_structured'):
            diary = visit.diary_structured or {}
            diary.update({
                'transcript': self.validated_data['raw_transcript'],
                'language': self.validated_data.get('language', 'ru'),
                'audio_duration': self.validated_data.get('audio_duration'),
                'metadata': self.validated_data.get('metadata', {}),
                'last_updated': timezone.now().isoformat(),
                'updated_by': user.get_full_name() if user else 'System'
            })
            
            # Merge structured data
            if structured:
                diary.update(structured)
            
            visit.diary_structured = diary
        
        # Update traditional fields if provided in structured_data
        if 'diagnosis' in structured:
            visit.diagnosis = structured['diagnosis']
        if 'treatment_plan' in structured:
            visit.treatment_plan = structured['treatment_plan']
        if 'comment' in structured:
            visit.comment = structured['comment']
        
        # Update status if still draft
        if visit.status == 'draft':
            visit.status = 'in_progress'
        
        visit.save()
        
        # TEMPORARILY DISABLED - ehr and consent apps not in container
        # # Create EHR record
        # from apps.ehr.models import EHRRecord
        # from django.contrib.contenttypes.models import ContentType
        # 
        # # Check if user is external (via grant)
        # is_external = not visit.appointment.patient.has_organization(user.organization) if user else False
        # 
        # # Get grant if external
        # grant = None
        # if is_external:
        #     from apps.consent.models import AccessGrant
        #     grant = AccessGrant.objects.filter(
        #         patient=visit.appointment.patient,
        #         grantee_org=user.organization,
        #         valid_from__lte=timezone.now(),
        #         valid_to__gte=timezone.now(),
        #         revoked_at__isnull=True
        #     ).first()
        # 
        # ehr_record = EHRRecord.objects.create(
        #     patient=visit.appointment.patient,
        #     organization=user.organization if user else visit.appointment.patient.organization,
        #     author=user,
        #     record_type='visit_note',
        #     title=f"Визит: {visit.appointment.service.name if visit.appointment.service else 'Прием'}",
        #     payload={
        #         'visit_id': visit.id,
        #         'appointment_id': visit.appointment.id,
        #         'raw_transcript': self.validated_data['raw_transcript'],
        #         'structured_data': structured,
        #         'language': self.validated_data.get('language', 'ru'),
        #         'audio_duration': self.validated_data.get('audio_duration'),
        #         'metadata': self.validated_data.get('metadata', {}),
        #         'created_via': 'desktop_dictation'
        #     },
        #     content_type=ContentType.objects.get_for_model(Visit),
        #     object_id=str(visit.id),
        #     is_external=is_external
        # )
        # 
        # # Log audit
        # if user:
        #     from apps.consent.models import AuditLog
        #     AuditLog.objects.create(
        #         user=user,
        #         organization=user.organization,
        #         patient=visit.appointment.patient,
        #         action='write',
        #         access_grant=grant,
        #         object_type='Visit',
        #         object_id=str(visit.id),
        #         ip_address=self.context.get('request').META.get('REMOTE_ADDR') if 'request' in self.context else None,
        #         user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', '') if 'request' in self.context else '',
        #         details={
        #             'ehr_record_id': str(ehr_record.id),
        #             'language': self.validated_data.get('language', 'ru'),
        #             'created_via': 'desktop_dictation'
        #         }
        #     )
        
        return visit

