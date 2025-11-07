from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.utils import timezone
from apps.core.permissions import IsBranchMember, CanAccessPatient
from .models import (
    Patient, Representative, PatientFile,
    PatientPhone, PatientSocialNetwork, PatientContactPerson,
    PatientDisease, PatientDiagnosis, PatientDoseLoad
)
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientSearchSerializer,
    RepresentativeSerializer,
    PatientFileSerializer,
    PatientPhoneSerializer,
    PatientSocialNetworkSerializer,
    PatientContactPersonSerializer,
    PatientDiseaseSerializer,
    PatientDiagnosisSerializer,
    PatientDoseLoadSerializer
)

# Import Sprint 2-5 models and serializers - migrations already applied (0006)
try:
    from .models import (
        MedicalExamination, MedExamPastDisease, 
        MedExamVaccination, MedExamLabTest, TreatmentPlan, 
        TreatmentStage, TreatmentStageItem, TreatmentPlanTemplate
    )
    from .serializers_extended import (
        MedicalExaminationSerializer, MedExamPastDiseaseSerializer,
        MedExamVaccinationSerializer, MedExamLabTestSerializer,
        TreatmentPlanSerializer, TreatmentStageSerializer,
        TreatmentStageItemSerializer, TreatmentPlanTemplateSerializer
    )
    EXTENDED_MODELS_AVAILABLE = True
except (ImportError, AttributeError):
    EXTENDED_MODELS_AVAILABLE = False

from .validators import validate_iin
import re


class PatientViewSet(viewsets.ModelViewSet):
    """
    Patient CRUD with deduplication
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        
        # Superusers see all patients
        if user.is_superuser:
            queryset = Patient.objects.all()
        elif user.organization:
            queryset = Patient.objects.filter(organizations=user.organization)
        else:
            # User without organization sees nothing
            queryset = Patient.objects.none()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name/phone/iin
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(iin__icontains=search)
            )
        
        # Prefetch related objects
        # Note: consent_history disabled until migrations are applied
        return queryset.prefetch_related(
            'organizations',
            'representatives', 'files', 'additional_phones', 'social_networks',
            'contact_persons', 'diseases', 'diagnoses', 'dose_loads'
            # 'consent_history'  # Uncomment after migrations
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanAccessPatient()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search for patients by phone or IIN (for deduplication)
        """
        serializer = PatientSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data.get('phone')
        iin = serializer.validated_data.get('iin')
        
        # Filter by organization
        if request.user.is_superuser:
            queryset = Patient.objects.all()
        elif request.user.organization:
            queryset = Patient.objects.filter(organizations=request.user.organization)
        else:
            queryset = Patient.objects.none()
        
        if phone:
            normalized = re.sub(r'\D', '', phone)
            queryset = queryset.filter(phone__iregex=f'[^0-9]*{normalized}[^0-9]*')
        
        if iin:
            queryset = queryset.filter(iin=iin)
        
        patients = queryset[:10]
        serializer = PatientListSerializer(patients, many=True)
        
        return Response({
            'found': patients.exists(),
            'count': patients.count(),
            'patients': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        """
        Add balance to patient account
        """
        patient = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        patient.balance += amount
        patient.save(update_fields=['balance'])
        
        return Response({
            'balance': float(patient.balance),
            'message': f'Added {amount} to balance'
        })
    
    @action(detail=True, methods=['post'])
    def verify_iin(self, request, pk=None):
        """
        Verify patient's IIN (Kazakhstan specific)
        """
        patient = self.get_object()
        
        if not patient.iin:
            return Response(
                {'error': 'ИИН не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate IIN using KZ algorithm
        validation_result = validate_iin(patient.iin)
        
        if validation_result['valid']:
            # Mark as verified
            patient.iin_verified = True
            patient.iin_verified_at = timezone.now()
            patient.save(update_fields=['iin_verified', 'iin_verified_at'])
            
            return Response({
                'valid': True,
                'iin': patient.iin,
                'birth_date': validation_result['birth_date'].isoformat() if validation_result['birth_date'] else None,
                'sex': validation_result['sex'],
                'verified_at': patient.iin_verified_at
            })
        else:
            return Response({
                'valid': False,
                'error': validation_result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # ============================================================================
    # TEMPORARILY DISABLED - Uncomment after migrations
    # ============================================================================
    # @action(detail=True, methods=['post'])
    # def save_consent(self, request, pk=None):
    #     """
    #     Save patient consent (KZ compliance - audit trail)
    #     """
    #     patient = self.get_object()
    #     consent_type = request.data.get('consent_type')
    #     status_value = request.data.get('status', 'accepted')
    #     
    #     if not consent_type:
    #         return Response(
    #             {'error': 'consent_type is required'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     
    #     # Get IP address
    #     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #     if x_forwarded_for:
    #         ip_address = x_forwarded_for.split(',')[0]
    #     else:
    #         ip_address = request.META.get('REMOTE_ADDR')
    #     
    #     # Get user agent
    #     user_agent = request.META.get('HTTP_USER_AGENT', '')
    #     
    #     # Create consent history entry
    #     consent_history = ConsentHistory.objects.create(
    #         patient=patient,
    #         consent_type=consent_type,
    #         status=status_value,
    #         ip_address=ip_address,
    #         user_agent=user_agent,
    #         accepted_by=request.user
    #     )
    #     
    #     # Update patient's consents field
    #     if not patient.consents:
    #         patient.consents = {}
    #     patient.consents[consent_type] = {
    #         'status': status_value,
    #         'date': timezone.now().isoformat(),
    #         'by': request.user.get_full_name()
    #     }
    #     patient.save(update_fields=['consents'])
    #     
    #     serializer = ConsentHistorySerializer(consent_history)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    # 
    # @action(detail=True, methods=['get'])
    # def consent_history(self, request, pk=None):
    #     """
    #     Get patient's consent history
    #     """
    #     patient = self.get_object()
    #     consents = patient.consent_history.all()
    #     serializer = ConsentHistorySerializer(consents, many=True)
    #     return Response(serializer.data)
    # ============================================================================
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get patient statistics (Sprint 4)
        Returns: total visits, revenue, average check, balance, etc.
        """
        from decimal import Decimal
        from apps.billing.models import Invoice
        from apps.calendar.models import Appointment
        
        patient = self.get_object()
        
        # Get all appointments
        appointments = Appointment.objects.filter(patient=patient)
        total_visits = appointments.filter(status='done').count()
        
        # Get all invoices
        invoices = Invoice.objects.filter(
            visit__appointment__patient=patient,
            status='paid'
        )
        
        total_revenue = sum(invoice.paid_amount for invoice in invoices) or Decimal('0')
        average_check = total_revenue / total_visits if total_visits > 0 else Decimal('0')
        
        # Last visit and next appointment
        last_visit = appointments.filter(status='done').order_by('-start_datetime').first()
        next_appointment = appointments.filter(
            status__in=['booked', 'confirmed'],
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime').first()
        
        return Response({
            'total_visits': total_visits,
            'total_revenue': float(total_revenue),
            'average_check': float(average_check),
            'balance': float(patient.balance),
            'last_visit_date': last_visit.start_datetime.date().isoformat() if last_visit else None,
            'next_appointment': next_appointment.start_datetime.isoformat() if next_appointment else None,
        })
    
    @action(detail=True, methods=['post'], url_path='ai-analysis')
    def ai_analysis(self, request, pk=None):
        """
        Generate AI-powered analysis for patient using Gemini AI
        Returns: AI analysis of patient's medical data
        """
        from .ai_service import get_ai_service
        
        patient = self.get_object()
        ai_service = get_ai_service()
        
        # Check if AI service is available
        if not ai_service.is_available():
            return Response(
                {
                    'success': False,
                    'error': 'AI сервис недоступен. Пожалуйста, настройте GEMINI_API_KEY.',
                    'analysis': None
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Prepare patient data for analysis
        patient_data = {
            'full_name': patient.full_name,
            'age': patient.age,
            'sex': patient.sex,
            'sex_display': patient.get_sex_display(),
            'medical_history': patient.medical_history or '',
            'allergies': patient.allergies or '',
            'notes': patient.notes or '',
            'blood_type': getattr(patient, 'blood_type', ''),
            'rh_factor': getattr(patient, 'rh_factor', ''),
            'disability_group': getattr(patient, 'disability_group', ''),
            'disability_notes': getattr(patient, 'disability_notes', ''),
        }
        
        # Add chronic diseases
        diseases = []
        for disease in patient.diseases.all():
            diseases.append({
                'name': disease.name,
                'icd_code': disease.icd_code.code if disease.icd_code else 'N/A',
                'notes': disease.notes or '',
                'diagnosed_date': disease.diagnosed_date.isoformat() if disease.diagnosed_date else None
            })
        patient_data['diseases'] = diseases
        
        # Add diagnoses
        diagnoses = []
        for diagnosis in patient.diagnoses.all():
            diagnoses.append({
                'diagnosis_text': diagnosis.diagnosis_text,
                'icd_code': diagnosis.icd_code.code if diagnosis.icd_code else 'N/A',
                'notes': diagnosis.notes or '',
                'date': diagnosis.date.isoformat() if diagnosis.date else None
            })
        patient_data['diagnoses'] = diagnoses
        
        # Generate AI analysis
        result = ai_service.generate_patient_analysis(patient_data)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='send-verification')
    def send_verification(self, request):
        """
        Отправить SMS код для верификации пациента по ИИН (имитация)
        Код всегда: 1234
        """
        from datetime import timedelta
        from .models import PatientVerification
        from .utils.encryption import hash_iin
        
        iin = request.data.get('iin')
        
        if not iin:
            return Response(
                {'error': 'ИИН обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        organization = request.user.organization
        if not organization:
            return Response(
                {'error': 'Пользователь не привязан к организации'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search for patient by IIN (global search, not organization-specific)
        iin_hash = hash_iin(iin)
        patient = Patient.objects.filter(
            models.Q(iin=iin) | models.Q(iin_hash=iin_hash)
        ).first()
        
        if not patient:
            return Response(
                {'error': 'Пациент с таким ИИН не найден в базе данных'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if patient already in this organization
        if patient.has_organization(organization):
            return Response(
                {'error': 'Пациент уже зарегистрирован в вашей организации'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old unverified codes for this IIN
        PatientVerification.objects.filter(
            patient_data__iin=iin,
            is_verified=False,
            organization=organization
        ).delete()
        
        # Create new verification (имитация - код всегда 1234)
        verification = PatientVerification.objects.create(
            organization=organization,
            phone=patient.phone,  # Use patient's phone
            verification_code='1234',  # Фиксированный код для имитации
            patient_data={'iin': iin, 'patient_id': patient.id},
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        return Response({
            'message': 'SMS код отправлен',
            'verification_id': verification.id,
            'phone': patient.phone,  # Return masked phone
            'patient_name': f"{patient.last_name} {patient.first_name}",
            'expires_in_seconds': 600,
            # В реальной системе это не возвращается, но для тестирования:
            'test_code': '1234'  # Для удобства тестирования
        })
    
    @action(detail=False, methods=['post'], url_path='verify-code')
    def verify_code(self, request):
        """
        Проверить SMS код и добавить пациента в организацию
        """
        from .models import PatientVerification
        
        verification_id = request.data.get('verification_id')
        code = request.data.get('code')
        
        if not verification_id or not code:
            return Response(
                {'error': 'verification_id и code обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = PatientVerification.objects.get(
                id=verification_id,
                is_verified=False
            )
        except PatientVerification.DoesNotExist:
            return Response(
                {'error': 'Верификация не найдена или уже использована'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify code
        success, message = verification.verify(code)
        
        if not success:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get original patient
        patient_id = verification.patient_data.get('patient_id')
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Пациент не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Add organization to patient (if not already added)
        if patient.add_organization(verification.organization):
            message = f'Пациент {patient.full_name} успешно добавлен в вашу организацию'
            status_code = status.HTTP_201_CREATED
        else:
            message = f'Пациент {patient.full_name} уже был в вашей организации'
            status_code = status.HTTP_200_OK
        
        # Mark verification as used
        verification.delete()
        
        return Response({
            'message': message,
            'patient': PatientSerializer(patient).data
        }, status=status_code)


class RepresentativeViewSet(viewsets.ModelViewSet):
    queryset = Representative.objects.all()
    serializer_class = RepresentativeSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = Representative.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class PatientFileViewSet(viewsets.ModelViewSet):
    queryset = PatientFile.objects.all()
    serializer_class = PatientFileSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientFile.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class PatientPhoneViewSet(viewsets.ModelViewSet):
    queryset = PatientPhone.objects.all()
    serializer_class = PatientPhoneSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientPhone.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class PatientSocialNetworkViewSet(viewsets.ModelViewSet):
    queryset = PatientSocialNetwork.objects.all()
    serializer_class = PatientSocialNetworkSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientSocialNetwork.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class PatientContactPersonViewSet(viewsets.ModelViewSet):
    queryset = PatientContactPerson.objects.all()
    serializer_class = PatientContactPersonSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientContactPerson.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class PatientDiseaseViewSet(viewsets.ModelViewSet):
    queryset = PatientDisease.objects.all()
    serializer_class = PatientDiseaseSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientDisease.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.select_related('icd_code', 'doctor')


class PatientDiagnosisViewSet(viewsets.ModelViewSet):
    queryset = PatientDiagnosis.objects.all()
    serializer_class = PatientDiagnosisSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientDiagnosis.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.select_related('icd_code', 'doctor')


class PatientDoseLoadViewSet(viewsets.ModelViewSet):
    queryset = PatientDoseLoad.objects.all()
    serializer_class = PatientDoseLoadSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = PatientDoseLoad.objects.filter(patient__organizations=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


# ============================================================================
# SPRINT 2-5 VIEWSETS - Enabled after migrations 0006
# ============================================================================


if not EXTENDED_MODELS_AVAILABLE:
    # Placeholder - models not available yet
    pass
else:
    # ==================== Sprint 3: Medical Examination ViewSets ====================

    class MedicalExaminationViewSet(viewsets.ModelViewSet):
        """Medical examination management"""
        queryset = MedicalExamination.objects.all()
        serializer_class = MedicalExaminationSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            patient_id = self.request.query_params.get('patient')
            queryset = MedicalExamination.objects.filter(patient__organizations=user.organization)
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            return queryset.select_related('patient', 'created_by').prefetch_related(
                'past_diseases', 'vaccinations', 'lab_tests'
            )
        
        def perform_create(self, serializer):
            serializer.save(created_by=self.request.user)


    class MedExamPastDiseaseViewSet(viewsets.ModelViewSet):
        queryset = MedExamPastDisease.objects.all()
        serializer_class = MedExamPastDiseaseSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            exam_id = self.request.query_params.get('examination')
            queryset = MedExamPastDisease.objects.filter(examination__patient__organizations=user.organization)
            if exam_id:
                queryset = queryset.filter(examination_id=exam_id)
            return queryset


    class MedExamVaccinationViewSet(viewsets.ModelViewSet):
        queryset = MedExamVaccination.objects.all()
        serializer_class = MedExamVaccinationSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            exam_id = self.request.query_params.get('examination')
            queryset = MedExamVaccination.objects.filter(examination__patient__organizations=user.organization)
            if exam_id:
                queryset = queryset.filter(examination_id=exam_id)
            return queryset


    class MedExamLabTestViewSet(viewsets.ModelViewSet):
        queryset = MedExamLabTest.objects.all()
        serializer_class = MedExamLabTestSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            exam_id = self.request.query_params.get('examination')
            queryset = MedExamLabTest.objects.filter(examination__patient__organizations=user.organization)
            if exam_id:
                queryset = queryset.filter(examination_id=exam_id)
            return queryset


    # ==================== Sprint 3: Treatment Plan ViewSets ====================


    class TreatmentPlanViewSet(viewsets.ModelViewSet):
        """Treatment plan management"""
        queryset = TreatmentPlan.objects.all()
        serializer_class = TreatmentPlanSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            patient_id = self.request.query_params.get('patient')
            queryset = TreatmentPlan.objects.filter(patient__organizations=user.organization)
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            return queryset.select_related('patient', 'created_by').prefetch_related(
                'stages__items__service'
            )
        
        def perform_create(self, serializer):
            serializer.save(created_by=self.request.user)
        
        @action(detail=True, methods=['post'])
        def freeze_prices(self, request, pk=None):
            """Freeze prices in the treatment plan"""
            plan = self.get_object()
            plan.total_cost_frozen = True
            plan.total_cost = plan.calculate_total_cost()
            plan.save(update_fields=['total_cost_frozen', 'total_cost'])
            
            serializer = self.get_serializer(plan)
            return Response(serializer.data)
        
        @action(detail=True, methods=['post'])
        def save_as_template(self, request, pk=None):
            """Save treatment plan as template"""
            plan = self.get_object()
            
            # Build template data from plan
            template_data = {
                'stages': []
            }
            
            for stage in plan.stages.all():
                stage_data = {
                    'title': stage.title,
                    'description': stage.description,
                    'items': []
                }
                
                for item in stage.items.all():
                    item_data = {
                        'service_id': item.service.id if item.service else None,
                        'description': item.description,
                        'qty_planned': float(item.qty_planned),
                        'unit_price': float(item.unit_price),
                        'discount_percent': float(item.discount_percent),
                    }
                    stage_data['items'].append(item_data)
                
                template_data['stages'].append(stage_data)
            
            # Create template
            template = TreatmentPlanTemplate.objects.create(
                organization=plan.patient.organization,
                name=request.data.get('name', f'Шаблон: {plan.title}'),
                description=request.data.get('description', plan.description),
                template_data=template_data,
                created_by=request.user
            )
            
            serializer = TreatmentPlanTemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


    class TreatmentStageViewSet(viewsets.ModelViewSet):
        queryset = TreatmentStage.objects.all()
        serializer_class = TreatmentStageSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            plan_id = self.request.query_params.get('plan')
            queryset = TreatmentStage.objects.filter(plan__patient__organizations=user.organization)
            if plan_id:
                queryset = queryset.filter(plan_id=plan_id)
            return queryset.prefetch_related('items')


    class TreatmentStageItemViewSet(viewsets.ModelViewSet):
        queryset = TreatmentStageItem.objects.all()
        serializer_class = TreatmentStageItemSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            stage_id = self.request.query_params.get('stage')
            queryset = TreatmentStageItem.objects.filter(stage__plan__patient__organizations=user.organization)
            if stage_id:
                queryset = queryset.filter(stage_id=stage_id)
            return queryset.select_related('service')


    class TreatmentPlanTemplateViewSet(viewsets.ModelViewSet):
        queryset = TreatmentPlanTemplate.objects.all()
        serializer_class = TreatmentPlanTemplateSerializer
        permission_classes = [IsAuthenticated, IsBranchMember]
        
        def get_queryset(self):
            user = self.request.user
            return TreatmentPlanTemplate.objects.filter(organization=user.organization)
        
        def perform_create(self, serializer):
            serializer.save(
                organization=self.request.user.organization,
                created_by=self.request.user
            )


"""
# OLD COMMENTED CODE - KEEPING FOR REFERENCE
class ConsentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    # Consent history ViewSet (read-only, created via PatientViewSet.save_consent)
    queryset = ConsentHistory.objects.all()
    serializer_class = ConsentHistorySerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = ConsentHistory.objects.filter(patient__organization=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.select_related('patient', 'accepted_by')


# ==================== Sprint 3: Medical Examination ViewSets ====================


class MedicalExaminationViewSet(viewsets.ModelViewSet):
    # Medical examination management
    queryset = MedicalExamination.objects.all()
    serializer_class = MedicalExaminationSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = MedicalExamination.objects.filter(patient__organization=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.select_related('patient', 'created_by').prefetch_related(
            'past_diseases', 'vaccinations', 'lab_tests'
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MedExamPastDiseaseViewSet(viewsets.ModelViewSet):
    queryset = MedExamPastDisease.objects.all()
    serializer_class = MedExamPastDiseaseSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        exam_id = self.request.query_params.get('examination')
        queryset = MedExamPastDisease.objects.filter(examination__patient__organization=user.organization)
        if exam_id:
            queryset = queryset.filter(examination_id=exam_id)
        return queryset


class MedExamVaccinationViewSet(viewsets.ModelViewSet):
    queryset = MedExamVaccination.objects.all()
    serializer_class = MedExamVaccinationSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        exam_id = self.request.query_params.get('examination')
        queryset = MedExamVaccination.objects.filter(examination__patient__organization=user.organization)
        if exam_id:
            queryset = queryset.filter(examination_id=exam_id)
        return queryset


class MedExamLabTestViewSet(viewsets.ModelViewSet):
    queryset = MedExamLabTest.objects.all()
    serializer_class = MedExamLabTestSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        exam_id = self.request.query_params.get('examination')
        queryset = MedExamLabTest.objects.filter(examination__patient__organization=user.organization)
        if exam_id:
            queryset = queryset.filter(examination_id=exam_id)
        return queryset


# ==================== Sprint 3: Treatment Plan ViewSets ====================


class TreatmentPlanViewSet(viewsets.ModelViewSet):
    # Treatment plan management
    queryset = TreatmentPlan.objects.all()
    serializer_class = TreatmentPlanSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = TreatmentPlan.objects.filter(patient__organization=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.select_related('patient', 'created_by').prefetch_related(
            'stages__items__service'
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def freeze_prices(self, request, pk=None):
        # Freeze prices in the treatment plan
        plan = self.get_object()
        plan.total_cost_frozen = True
        plan.total_cost = plan.calculate_total_cost()
        plan.save(update_fields=['total_cost_frozen', 'total_cost'])
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def save_as_template(self, request, pk=None):
        # Save treatment plan as template
        plan = self.get_object()
        
        # Build template data from plan
        template_data = {
            'stages': []
        }
        
        for stage in plan.stages.all():
            stage_data = {
                'title': stage.title,
                'description': stage.description,
                'items': []
            }
            
            for item in stage.items.all():
                item_data = {
                    'service_id': item.service.id if item.service else None,
                    'description': item.description,
                    'qty_planned': float(item.qty_planned),
                    'unit_price': float(item.unit_price),
                    'discount_percent': float(item.discount_percent),
                }
                stage_data['items'].append(item_data)
            
            template_data['stages'].append(stage_data)
        
        # Create template
        template = TreatmentPlanTemplate.objects.create(
            organization=plan.patient.organization,
            name=request.data.get('name', f'Шаблон: {plan.title}'),
            description=request.data.get('description', plan.description),
            template_data=template_data,
            created_by=request.user
        )
        
        serializer = TreatmentPlanTemplateSerializer(template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TreatmentStageViewSet(viewsets.ModelViewSet):
    queryset = TreatmentStage.objects.all()
    serializer_class = TreatmentStageSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        plan_id = self.request.query_params.get('plan')
        queryset = TreatmentStage.objects.filter(plan__patient__organization=user.organization)
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
        return queryset.prefetch_related('items')


class TreatmentStageItemViewSet(viewsets.ModelViewSet):
    queryset = TreatmentStageItem.objects.all()
    serializer_class = TreatmentStageItemSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        stage_id = self.request.query_params.get('stage')
        queryset = TreatmentStageItem.objects.filter(stage__plan__patient__organization=user.organization)
        if stage_id:
            queryset = queryset.filter(stage_id=stage_id)
        return queryset.select_related('service')


class TreatmentPlanTemplateViewSet(viewsets.ModelViewSet):
    queryset = TreatmentPlanTemplate.objects.all()
    serializer_class = TreatmentPlanTemplateSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        return TreatmentPlanTemplate.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
"""

# End of temporarily disabled ViewSets
# Uncomment above after migrations are applied


from rest_framework import generics


# TEMPORARILY DISABLED - consent app not in container
class PatientByGrantView(generics.RetrieveAPIView):
    """
    Get patient details by active grant ID (for desktop app)
    GET /api/v1/patients/by-grant/{grant_id}/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer
    
    def get_object(self):
        from apps.consent.models import AccessGrant, AuditLog
        from django.shortcuts import get_object_or_404
        
        grant_id = self.kwargs.get('grant_id')
        user = self.request.user
        
        # Get grant and verify it belongs to user's org and is active
        grant = get_object_or_404(
            AccessGrant,
            id=grant_id,
            grantee_org=user.organization,
            revoked_at__isnull=True
        )
        
        # Check if grant is still valid
        if not grant.is_active():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Grant has expired')
        
        # Track access
        grant.track_access()
        
        # Log audit
        try:
            AuditLog.objects.create(
                user=user,
                organization=user.organization,
                patient=grant.patient,
                action='read',
                access_grant=grant,
                object_type='Patient',
                object_id=str(grant.patient.id),
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'grant_id': str(grant.id),
                    'accessed_via': 'desktop_app'
                }
            )
        except Exception as e:
            # Log audit error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to create audit log: {e}')
        
        return grant.patient