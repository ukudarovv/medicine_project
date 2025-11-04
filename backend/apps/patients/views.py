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

# Import Sprint 2-5 models and serializers only after migrations
# These imports are moved inside ViewSets to prevent import errors before migrations
# from .models import (
#     ConsentHistory, MedicalExamination, MedExamPastDisease, 
#     MedExamVaccination, MedExamLabTest, TreatmentPlan, 
#     TreatmentStage, TreatmentStageItem, TreatmentPlanTemplate
# )
# from .serializers import ConsentHistorySerializer
# from .serializers_extended import (
#     MedicalExaminationSerializer, MedExamPastDiseaseSerializer,
#     MedExamVaccinationSerializer, MedExamLabTestSerializer,
#     TreatmentPlanSerializer, TreatmentStageSerializer,
#     TreatmentStageItemSerializer, TreatmentPlanTemplateSerializer
# )
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
        queryset = Patient.objects.filter(organization=user.organization)
        
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
        return queryset.select_related('organization').prefetch_related(
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
        
        queryset = Patient.objects.filter(organization=request.user.organization)
        
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


class RepresentativeViewSet(viewsets.ModelViewSet):
    queryset = Representative.objects.all()
    serializer_class = RepresentativeSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = Representative.objects.filter(patient__organization=user.organization)
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
        queryset = PatientFile.objects.filter(patient__organization=user.organization)
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
        queryset = PatientPhone.objects.filter(patient__organization=user.organization)
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
        queryset = PatientSocialNetwork.objects.filter(patient__organization=user.organization)
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
        queryset = PatientContactPerson.objects.filter(patient__organization=user.organization)
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
        queryset = PatientDisease.objects.filter(patient__organization=user.organization)
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
        queryset = PatientDiagnosis.objects.filter(patient__organization=user.organization)
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
        queryset = PatientDoseLoad.objects.filter(patient__organization=user.organization)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


# ============================================================================
# SPRINT 2-5 VIEWSETS TEMPORARILY DISABLED
# ============================================================================
# The following ViewSets are commented out until migrations are applied.
# After running migrations, uncomment all code below and update urls.py
# 
# ViewSets included:
# - ConsentHistoryViewSet
# - MedicalExaminationViewSet + related (PastDisease, Vaccination, LabTest)
# - TreatmentPlanViewSet + related (Stage, StageItem, Template)
#
# To enable:
# 1. Apply migrations: python manage.py migrate
# 2. Uncomment all code below (lines 400-599)
# 3. Uncomment imports at top of file (lines 29-40)
# 4. Uncomment routes in urls.py
# ============================================================================

"""
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
