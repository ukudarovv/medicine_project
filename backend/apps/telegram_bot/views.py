"""
API Views for Telegram Bot
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta, time as dt_time
from django.db.models import Q

from .models import (
    PatientTelegramLink,
    BotBroadcast,
    BotDocument,
    BotFeedback,
    SupportTicket
)
from .serializers import (
    PatientUpsertSerializer,
    PatientTelegramLinkSerializer,
    BranchSerializer,
    ServiceSerializer,
    DoctorSerializer,
    TimeSlotSerializer,
    AppointmentCreateSerializer,
    AppointmentSerializer,
    BotDocumentSerializer,
    BotFeedbackCreateSerializer,
    SupportTicketCreateSerializer,
    BotBroadcastSerializer
)
from .permissions import BotAPIAuthentication, IsBotAuthenticated

from apps.patients.models import Patient
from apps.patients.validators import validate_iin
from apps.org.models import Branch, Organization
from apps.services.models import Service
from apps.staff.models import Employee
from apps.calendar.models import Appointment, Availability
from apps.billing.services.kaspi_integration import get_kaspi_service
from apps.telegram_bot.services.document_generator import DocumentGenerator
from apps.telegram_bot.services.segmentation import PatientSegmentation
from apps.telegram_bot.tasks import process_broadcast


# ==================== Patient Management ====================

class PatientUpsertView(APIView):
    """
    Create or update patient via Telegram bot
    POST /api/bot/patient/upsert/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        serializer = PatientUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        telegram_user_id = data['telegram_user_id']
        
        # Check if telegram link exists
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = tg_link.patient
            created = False
        except PatientTelegramLink.DoesNotExist:
            # Create new patient
            organization = get_object_or_404(Organization, id=data['organization_id'])
            
            patient = Patient.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                middle_name=data.get('middle_name', ''),
                phone=data['phone'],
                birth_date=data['birth_date'],
                sex=data['sex'],
                iin=data.get('iin', '')
            )
            
            # Add organization to many-to-many relationship
            patient.organizations.add(organization)
            
            # Create telegram link
            tg_link = PatientTelegramLink.objects.create(
                patient=patient,
                telegram_user_id=telegram_user_id,
                telegram_username=data.get('telegram_username', ''),
                language=data.get('language', 'ru'),
                consents_json=data.get('consents', {})
            )
            created = True
        
        # Update existing patient
        if not created:
            patient.first_name = data['first_name']
            patient.last_name = data['last_name']
            patient.middle_name = data.get('middle_name', '')
            patient.phone = data['phone']
            patient.birth_date = data['birth_date']
            patient.sex = data['sex']
            if data.get('iin'):
                patient.iin = data['iin']
            patient.save()
            
            tg_link.telegram_username = data.get('telegram_username', '')
            tg_link.language = data.get('language', 'ru')
            if data.get('consents'):
                tg_link.consents_json.update(data['consents'])
            tg_link.save()
        
        return Response({
            'patient_id': patient.id,
            'telegram_link_id': str(tg_link.id),
            'created': created,
            'full_name': patient.full_name
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class VerifyIINView(APIView):
    """
    Verify IIN
    POST /api/bot/patient/verify-iin/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        iin = request.data.get('iin')
        if not iin:
            return Response({'error': 'IIN is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = validate_iin(iin)
        return Response(result)


class GetPatientByTelegramView(APIView):
    """
    Get patient by telegram user ID
    GET /api/bot/patient/by-telegram/<telegram_user_id>/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request, telegram_user_id):
        try:
            tg_link = PatientTelegramLink.objects.select_related('patient').get(
                telegram_user_id=telegram_user_id
            )
            serializer = PatientTelegramLinkSerializer(tg_link)
            return Response(serializer.data)
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Booking ====================

class BranchListView(generics.ListAPIView):
    """
    List branches
    GET /api/bot/branches/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    serializer_class = BranchSerializer
    
    def get_queryset(self):
        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            return Branch.objects.filter(organization_id=organization_id, is_active=True)
        return Branch.objects.filter(is_active=True)


class ServiceListView(generics.ListAPIView):
    """
    List services
    GET /api/bot/services/?branch_id=1
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        
        branch_id = self.request.query_params.get('branch_id')
        if branch_id:
            queryset = queryset.filter(branches__id=branch_id)
        
        return queryset.distinct()


class DoctorListView(generics.ListAPIView):
    """
    List doctors for a service
    GET /api/bot/doctors/?service_id=1&date=2025-11-10
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    serializer_class = DoctorSerializer
    
    def get_queryset(self):
        service_id = self.request.query_params.get('service_id')
        date_str = self.request.query_params.get('date')
        
        queryset = Employee.objects.filter(
            is_active=True,
            role__in=['doctor', 'therapist', 'specialist']
        )
        
        if service_id:
            queryset = queryset.filter(services__id=service_id)
        
        # Filter by availability on specific date
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                weekday = date.weekday()
                queryset = queryset.filter(availabilities__weekday=weekday, availabilities__is_active=True)
            except ValueError:
                pass
        
        return queryset.distinct()


class AvailableSlotsView(APIView):
    """
    Get available time slots for doctor
    GET /api/bot/slots/?doctor_id=1&date=2025-11-10
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')
        
        if not doctor_id or not date_str:
            return Response({'error': 'doctor_id and date are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            doctor = Employee.objects.get(id=doctor_id)
        except (ValueError, Employee.DoesNotExist):
            return Response({'error': 'Invalid doctor or date'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get doctor's availability for this weekday
        weekday = date.weekday()
        availabilities = Availability.objects.filter(
            employee=doctor,
            weekday=weekday,
            is_active=True
        )
        
        if not availabilities.exists():
            return Response({'slots': []})
        
        # Get existing appointments for this date
        existing_appointments = Appointment.objects.filter(
            employee=doctor,
            date=date,
            status__in=['scheduled', 'confirmed']
        )
        
        # Generate time slots
        slots = []
        for availability in availabilities:
            current_time = availability.time_from
            end_time = availability.time_to
            
            while current_time < end_time:
                # Check if this slot is available
                is_available = not existing_appointments.filter(
                    time_from__lte=current_time,
                    time_to__gt=current_time
                ).exists()
                
                slots.append({
                    'time': current_time.strftime('%H:%M'),
                    'available': is_available
                })
                
                # Increment by 30 minutes (or service duration)
                current_time = (datetime.combine(date, current_time) + timedelta(minutes=30)).time()
        
        return Response({'slots': slots})


# ==================== Appointments ====================

class AppointmentCreateView(APIView):
    """
    Create appointment
    POST /api/bot/appointments/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Get patient by telegram ID
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=data['telegram_user_id'])
            patient = tg_link.patient
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get related objects
        employee = get_object_or_404(Employee, id=data['employee_id'])
        service = get_object_or_404(Service, id=data['service_id'])
        branch = get_object_or_404(Branch, id=data['branch_id'])
        
        # Calculate end time
        duration = service.duration_minutes or 30
        start_datetime = datetime.combine(data['date'], data['time'])
        end_time = (start_datetime + timedelta(minutes=duration)).time()
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            employee=employee,
            service=service,
            branch=branch,
            date=data['date'],
            time_from=data['time'],
            time_to=end_time,
            notes=data.get('notes', ''),
            status='scheduled'
        )
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyAppointmentsView(generics.ListAPIView):
    """
    Get my appointments
    GET /api/bot/appointments/my/?telegram_user_id=123456
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        telegram_user_id = self.request.query_params.get('telegram_user_id')
        if not telegram_user_id:
            return Appointment.objects.none()
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = tg_link.patient
        except PatientTelegramLink.DoesNotExist:
            return Appointment.objects.none()
        
        # Get future and recent past appointments
        today = timezone.now().date()
        past_threshold = today - timedelta(days=30)
        
        return Appointment.objects.filter(
            patient=patient,
            date__gte=past_threshold
        ).select_related('employee', 'service', 'branch').order_by('-date', '-time_from')


class AppointmentUpdateView(APIView):
    """
    Update appointment (reschedule)
    PATCH /api/bot/appointments/<id>/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def patch(self, request, pk):
        appointment = get_object_or_404(Appointment, id=pk)
        
        # Update fields
        if 'date' in request.data:
            appointment.date = request.data['date']
        if 'time' in request.data:
            appointment.time_from = request.data['time']
            # Recalculate end time
            duration = appointment.service.duration_minutes or 30
            start_datetime = datetime.combine(appointment.date, appointment.time_from)
            appointment.time_to = (start_datetime + timedelta(minutes=duration)).time()
        
        appointment.save()
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)


class AppointmentCancelView(APIView):
    """
    Cancel appointment
    POST /api/bot/appointments/<id>/cancel/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, id=pk)
        appointment.status = 'cancelled'
        appointment.save()
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)


# ==================== Documents ====================

class DocumentListView(generics.ListAPIView):
    """
    List documents for patient
    GET /api/bot/documents/?telegram_user_id=123456&type=direction
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    serializer_class = BotDocumentSerializer
    
    def get_queryset(self):
        telegram_user_id = self.request.query_params.get('telegram_user_id')
        doc_type = self.request.query_params.get('type')
        
        if not telegram_user_id:
            return BotDocument.objects.none()
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = tg_link.patient
        except PatientTelegramLink.DoesNotExist:
            return BotDocument.objects.none()
        
        queryset = BotDocument.objects.filter(patient=patient, is_expired=False)
        
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        return queryset.order_by('-created_at')


class DocumentGenerateView(APIView):
    """
    Generate document
    POST /api/bot/documents/generate/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        telegram_user_id = request.data.get('telegram_user_id')
        doc_type = request.data.get('document_type')
        language = request.data.get('language', 'ru')
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = tg_link.patient
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate document based on type
        if doc_type == 'tax':
            year = request.data.get('year', timezone.now().year)
            doc = DocumentGenerator.generate_tax_certificate(patient, year, language)
        else:
            return Response({'error': 'Unsupported document type'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BotDocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentDownloadView(APIView):
    """
    Get download URL for document
    GET /api/bot/documents/<uuid>/download/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request, pk):
        doc = get_object_or_404(BotDocument, id=pk)
        
        if doc.is_expired:
            return Response({'error': 'Document expired'}, status=status.HTTP_410_GONE)
        
        # Return file path (in production, this would be a presigned URL)
        from django.conf import settings
        file_url = f"{settings.MEDIA_URL}{doc.file_path}"
        
        return Response({
            'download_url': file_url,
            'expires_at': doc.expires_at,
            'filename': doc.title + '.pdf'
        })


# ==================== Payments ====================

class CreateInvoiceView(APIView):
    """
    Create payment invoice
    POST /api/bot/payments/invoice/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        from apps.billing.models import Invoice
        
        telegram_user_id = request.data.get('telegram_user_id')
        amount = request.data.get('amount')
        description = request.data.get('description', '')
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = tg_link.patient
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Mock invoice creation (simplified)
        invoice_id = f"INV-{patient.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get Kaspi QR (mock)
        try:
            kaspi = get_kaspi_service(patient.organization)
            qr_result = kaspi.generate_qr(invoice_id, amount, description)
        except:
            # Fallback mock
            qr_result = {
                'success': True,
                'qr_code_url': f'https://test.kaspi.kz/qr/{invoice_id}',
                'payment_id': f'KASPI_TEST_{invoice_id}',
                'amount': float(amount),
                'status': 'pending'
            }
        
        return Response({
            'invoice_id': invoice_id,
            'amount': amount,
            'qr_code_url': qr_result.get('qr_code_url'),
            'payment_id': qr_result.get('payment_id'),
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    """
    Get payment status
    GET /api/bot/payments/<id>/status/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request, pk):
        # Mock implementation
        return Response({
            'invoice_id': pk,
            'status': 'pending',
            'amount': 0,
            'paid_at': None
        })


class PaymentCallbackView(APIView):
    """
    Payment webhook callback
    POST /api/bot/payments/callback/
    """
    permission_classes = [AllowAny]  # Webhook from payment provider
    
    def post(self, request):
        # Handle payment callback from Kaspi/Halyk
        # This would verify signature and update invoice status
        return Response({'status': 'ok'})


class PatientBalanceView(APIView):
    """
    Get patient balance
    GET /api/bot/payments/balance/?telegram_user_id=123456
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request):
        telegram_user_id = request.query_params.get('telegram_user_id')
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = tg_link.patient
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'balance': float(patient.balance),
            'currency': 'KZT'
        })


# ==================== Feedback ====================

class FeedbackCreateView(APIView):
    """
    Create NPS feedback
    POST /api/bot/feedback/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        serializer = BotFeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=data['telegram_user_id'])
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        appointment = get_object_or_404(Appointment, id=data['appointment_id'])
        
        feedback = BotFeedback.objects.create(
            appointment=appointment,
            patient_telegram_link=tg_link,
            score=data['score'],
            comment=data.get('comment', '')
        )
        
        return Response({
            'id': str(feedback.id),
            'score': feedback.score,
            'is_low_score': feedback.is_low_score
        }, status=status.HTTP_201_CREATED)


# ==================== Support ====================

class SupportTicketCreateView(APIView):
    """
    Create support ticket
    POST /api/bot/support/ticket/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        serializer = SupportTicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=data['telegram_user_id'])
        except PatientTelegramLink.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ticket = SupportTicket.objects.create(
            patient_telegram_link=tg_link,
            subject=data['subject'],
            message=data['message'],
            status='open'
        )
        
        return Response({
            'ticket_id': str(ticket.id),
            'subject': ticket.subject,
            'status': ticket.status
        }, status=status.HTTP_201_CREATED)


class FAQListView(APIView):
    """
    Get FAQ list
    GET /api/bot/support/faq/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request):
        # Mock FAQ data
        faqs = [
            {'question': 'Как записаться на приём?', 'answer': 'Используйте кнопку "Записаться" в меню бота'},
            {'question': 'Как отменить запись?', 'answer': 'Перейдите в "Мои записи" и выберите нужную запись'},
            {'question': 'Где посмотреть результаты анализов?', 'answer': 'В разделе "Документы" → "Результаты"'},
        ]
        return Response({'faqs': faqs})


# ==================== Broadcasts ====================

class BroadcastCreateView(APIView):
    """
    Create broadcast (admin only)
    POST /api/bot/broadcast/create/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request):
        serializer = BotBroadcastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        broadcast = serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BroadcastStartView(APIView):
    """
    Start broadcast
    POST /api/bot/broadcast/<uuid>/start/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request, pk):
        broadcast = get_object_or_404(BotBroadcast, id=pk)
        
        if broadcast.status != 'draft':
            return Response({'error': 'Broadcast already started'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Start processing in background
        process_broadcast.delay(str(broadcast.id))
        
        broadcast.status = 'scheduled'
        broadcast.save()
        
        return Response({'status': 'started'})


class BroadcastStatsView(APIView):
    """
    Get broadcast statistics
    GET /api/bot/broadcast/<uuid>/stats/
    """
    authentication_classes = [BotAPIAuthentication]
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request, pk):
        broadcast = get_object_or_404(BotBroadcast, id=pk)
        
        return Response({
            'total_recipients': broadcast.total_recipients,
            'sent_count': broadcast.sent_count,
            'delivered_count': broadcast.delivered_count,
            'failed_count': broadcast.failed_count,
            'clicked_count': broadcast.clicked_count,
            'status': broadcast.status
        })


# ==================== Consent Management (for bot) ====================

class DenyAccessRequestView(APIView):
    """
    Deny access request (called from Telegram bot)
    POST /api/bot/consent/access-requests/{uuid}/deny/
    """
    permission_classes = [IsBotAuthenticated]
    
    def post(self, request, pk):
        from apps.consent.models import AccessRequest, AuditLog
        
        access_request = get_object_or_404(AccessRequest, pk=pk)
        
        if access_request.status != 'pending':
            return Response(
                {'error': 'Request already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        access_request.status = 'denied'
        access_request.responded_at = timezone.now()
        access_request.save()
        
        # Record denial for rate limiting
        from apps.consent.rate_limiting import ConsentRateLimiter
        ConsentRateLimiter.record_denial(
            access_request.requester_org_id,
            access_request.patient_id
        )
        
        # Log
        AuditLog.objects.create(
            user=None,
            organization=access_request.requester_org,
            patient=access_request.patient,
            action='deny',
            details={'access_request_id': str(access_request.id)}
        )
        
        return Response({
            'success': True,
            'org_name': access_request.requester_org.name
        })


class AccessRequestDetailView(APIView):
    """
    Get access request details (called from Telegram bot)
    GET /api/bot/consent/access-requests/{uuid}/
    """
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request, pk):
        from apps.consent.models import AccessRequest
        
        access_request = get_object_or_404(AccessRequest, pk=pk)
        
        return Response({
            'success': True,
            'request': {
                'id': str(access_request.id),
                'requester_org_name': access_request.requester_org.name,
                'requester_user_name': access_request.requester_user.get_full_name() if access_request.requester_user else None,
                'reason': access_request.reason,
                'scopes': access_request.scopes,
                'requested_duration_days': access_request.requested_duration_days,
                'status': access_request.status,
                'created_at': access_request.created_at.isoformat(),
            }
        })


class PatientGrantsView(APIView):
    """
    Get patient's access grants (called from Telegram bot)
    GET /api/bot/consent/patient-grants/{telegram_user_id}/
    """
    permission_classes = [IsBotAuthenticated]
    
    def get(self, request, telegram_user_id):
        from apps.consent.models import AccessGrant
        
        try:
            link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            patient = link.patient
        except PatientTelegramLink.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Patient not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get active grants
        grants = AccessGrant.objects.filter(
            patient=patient,
            revoked_at__isnull=True
        ).select_related('grantee_org')
        
        grants_data = []
        for grant in grants:
            grants_data.append({
                'id': str(grant.id),
                'grantee_org_name': grant.grantee_org.name,
                'scopes': grant.scopes,
                'valid_from': grant.valid_from.isoformat(),
                'valid_to': grant.valid_to.isoformat(),
                'is_active': grant.is_active(),
                'is_whitelist': grant.is_whitelist,
                'last_accessed_at': grant.last_accessed_at.isoformat() if grant.last_accessed_at else None,
                'access_count': grant.access_count,
                'created_at': grant.created_at.isoformat(),
            })
        
        return Response({
            'success': True,
            'grants': grants_data
        })


# ==================== Webhook ====================

class TelegramWebhookView(APIView):
    """
    Telegram webhook endpoint
    POST /api/bot/webhook/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # This endpoint receives updates from Telegram
        # In production, this would be processed by the bot service
        # For now, just acknowledge receipt
        return Response({'ok': True})

