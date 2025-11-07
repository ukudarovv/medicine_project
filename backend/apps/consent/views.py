"""
Views for consent system API
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from apps.patients.models import Patient
from apps.patients.utils.encryption import hash_iin
from .models import AccessRequest, AccessGrant, AuditLog
from .serializers import (
    PatientSearchSerializer,
    PatientSearchResultSerializer,
    AccessRequestSerializer,
    OTPVerifySerializer,
    AccessGrantSerializer,
    AuditLogSerializer
)
from .permissions import CanRequestAccess


class PatientSearchView(generics.GenericAPIView):
    """
    Search for patient by IIN
    POST /api/v1/consent/search-patient
    """
    permission_classes = [IsAuthenticated, CanRequestAccess]
    serializer_class = PatientSearchSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        iin = serializer.validated_data['iin']
        iin_hash_value = hash_iin(iin)
        
        # Find patient by IIN hash
        try:
            patient = Patient.objects.get(iin_hash=iin_hash_value)
            
            # Return minimal patient data
            result_serializer = PatientSearchResultSerializer(patient)
            return Response(result_serializer.data)
        
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Пациент с таким ИИН не найден'},
                status=status.HTTP_404_NOT_FOUND
            )


class AccessRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing access requests
    """
    serializer_class = AccessRequestSerializer
    permission_classes = [IsAuthenticated, CanRequestAccess]
    
    def get_queryset(self):
        user = self.request.user
        org = user.organization
        
        # Filter by organization
        queryset = AccessRequest.objects.filter(
            requester_org=org
        ).select_related(
            'patient', 'requester_org', 'requester_user'
        )
        
        # Filter by patient if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by status if provided
        request_status = self.request.query_params.get('status')
        if request_status:
            queryset = queryset.filter(status=request_status)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """
        Deny an access request
        Only callable by patient (via Telegram bot API)
        """
        access_request = self.get_object()
        
        if access_request.status != 'pending':
            return Response(
                {'error': 'Запрос уже обработан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        access_request.status = 'denied'
        access_request.responded_at = timezone.now()
        access_request.save(update_fields=['status', 'responded_at'])
        
        # Record denial for rate limiting
        from apps.consent.rate_limiting import ConsentRateLimiter
        ConsentRateLimiter.record_denial(
            access_request.requester_org_id,
            access_request.patient_id
        )
        
        # Log action
        AuditLog.objects.create(
            user=None,  # Patient action
            organization=access_request.requester_org,
            patient=access_request.patient,
            action='deny',
            details={
                'access_request_id': str(access_request.id),
                'reason': access_request.reason
            }
        )
        
        return Response({'status': 'denied'})


class OTPVerifyView(generics.GenericAPIView):
    """
    Verify OTP and create access grant
    POST /api/v1/consent/otp/verify
    
    This endpoint is typically called by the Telegram bot backend
    """
    permission_classes = [AllowAny]  # Bot will use API secret for auth
    serializer_class = OTPVerifySerializer
    
    def post(self, request):
        # Verify API secret from Telegram bot
        from django.conf import settings
        api_secret = request.headers.get('X-Bot-Secret')
        expected_secret = getattr(settings, 'TELEGRAM_BOT_API_SECRET', '')
        
        if api_secret != expected_secret:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create grant
        grant = serializer.create_grant()
        
        # Return grant details
        grant_serializer = AccessGrantSerializer(grant)
        return Response(grant_serializer.data, status=status.HTTP_201_CREATED)


class AccessGrantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing access grants
    """
    serializer_class = AccessGrantSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_queryset(self):
        user = self.request.user
        org = user.organization
        
        # Get grants where user's org is the grantee
        queryset = AccessGrant.objects.filter(
            grantee_org=org,
            revoked_at__isnull=True
        ).select_related(
            'patient', 'grantee_org'
        )
        
        # Filter by patient if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter active only
        if self.request.query_params.get('active_only') == 'true':
            from django.utils import timezone
            now = timezone.now()
            queryset = queryset.filter(
                valid_from__lte=now,
                valid_to__gte=now
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke an access grant
        """
        grant = self.get_object()
        
        if grant.revoked_at:
            return Response(
                {'error': 'Грант уже отозван'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        grant.revoke(user=request.user, reason=reason)
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            organization=request.user.organization,
            patient=grant.patient,
            action='revoke',
            access_grant=grant,
            details={
                'grant_id': str(grant.id),
                'reason': reason
            }
        )
        
        return Response({'status': 'revoked'})
    
    @action(detail=False, methods=['post'])
    def create_whitelist(self, request):
        """
        Create long-term whitelist access grant
        Typically called by patient through Telegram bot
        """
        patient_id = request.data.get('patient_id')
        org_id = request.data.get('organization_id')
        scopes = request.data.get('scopes', ['read_summary', 'read_records'])
        duration_days = request.data.get('duration_days', 180)  # Default 6 months
        
        if not patient_id or not org_id:
            return Response(
                {'error': 'patient_id и organization_id обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.patients.models import Patient
        from apps.org.models import Organization
        
        try:
            patient = Patient.objects.get(id=patient_id)
            org = Organization.objects.get(id=org_id)
        except (Patient.DoesNotExist, Organization.DoesNotExist):
            return Response(
                {'error': 'Пациент или организация не найдены'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create whitelist grant
        from datetime import timedelta
        valid_from = timezone.now()
        valid_to = valid_from + timedelta(days=duration_days)
        
        grant = AccessGrant.objects.create(
            patient=patient,
            grantee_org=org,
            scopes=scopes,
            valid_from=valid_from,
            valid_to=valid_to,
            is_whitelist=True,
            created_by='patient'
        )
        
        # Log action
        AuditLog.objects.create(
            user=None,  # Patient action
            organization=org,
            patient=patient,
            action='share',
            access_grant=grant,
            details={
                'grant_id': str(grant.id),
                'scopes': grant.scopes,
                'valid_to': grant.valid_to.isoformat(),
                'is_whitelist': True
            }
        )
        
        serializer = self.get_serializer(grant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_grants(self, request):
        """
        Get patient's own access grants
        Typically called by patient through Telegram bot
        """
        telegram_user_id = request.query_params.get('telegram_user_id')
        if not telegram_user_id:
            return Response(
                {'error': 'telegram_user_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.telegram_bot.models import PatientTelegramLink
        
        try:
            link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = link.patient
        except PatientTelegramLink.DoesNotExist:
            return Response(
                {'error': 'Пациент не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all grants for this patient
        grants = AccessGrant.objects.filter(
            patient=patient,
            revoked_at__isnull=True
        ).select_related('grantee_org').order_by('-created_at')
        
        serializer = self.get_serializer(grants, many=True)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        org = user.organization
        
        # Filter by organization
        queryset = AuditLog.objects.filter(
            organization=org
        ).select_related(
            'user', 'organization', 'patient'
        )
        
        # Filter by patient if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by action if provided
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-created_at')


# Import timezone for use in deny action
from django.utils import timezone


class AccessRequestStatusView(generics.RetrieveAPIView):
    """
    Get status of access request (for desktop polling)
    GET /api/v1/consent/access-requests/{id}/status/
    """
    permission_classes = [IsAuthenticated, CanRequestAccess]
    serializer_class = AccessRequestSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        user = self.request.user
        org = user.organization
        return AccessRequest.objects.filter(requester_org=org)
    
    def retrieve(self, request, *args, **kwargs):
        access_request = self.get_object()
        
        # Check if expired
        if access_request.is_expired():
            access_request.mark_expired()
        
        # Base response
        response_data = {
            'id': str(access_request.id),
            'status': access_request.status,
            'status_display': access_request.get_status_display(),
            'created_at': access_request.created_at.isoformat(),
            'expires_at': access_request.expires_at.isoformat(),
            'delivery_channel': access_request.delivery_channel,
        }
        
        # If approved, include grant and patient context
        if access_request.status == 'approved':
            try:
                grant = access_request.grant
                response_data['grant'] = {
                    'grant_id': str(grant.id),
                    'valid_to': grant.valid_to.isoformat(),
                    'scopes': grant.scopes,
                }
                
                # Patient context for desktop
                patient = access_request.patient
                response_data['patient_context'] = {
                    'patient_id': patient.id,
                    'full_name': patient.full_name,
                    'age': patient.age,
                    'birth_date': patient.birth_date.isoformat(),
                    'sex': patient.sex,
                    'iin_masked': patient.iin_masked,
                    'osms_status': patient.osms_status,
                }
                
                # Check for active visit
                from apps.calendar.models import Appointment
                from apps.visits.models import Visit
                today = timezone.now().date()
                
                # Find today's appointments for this patient and doctor
                appointment = Appointment.objects.filter(
                    patient=patient,
                    employee=request.user,
                    start_datetime__date=today,
                    status__in=['scheduled', 'confirmed', 'in_progress']
                ).order_by('-start_datetime').first()
                
                if appointment:
                    response_data['patient_context']['appointment_id'] = appointment.id
                    # Check if visit exists
                    try:
                        visit = appointment.visit
                        response_data['patient_context']['visit_id'] = visit.id
                    except Visit.DoesNotExist:
                        response_data['patient_context']['visit_id'] = None
                else:
                    response_data['patient_context']['appointment_id'] = None
                    response_data['patient_context']['visit_id'] = None
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error getting patient context: {e}')
        
        return Response(response_data)
