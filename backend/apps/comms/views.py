from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsMarketer
from .models import (
    Template, MessageLog, Campaign, Reminder, Message,
    ContactLog, SmsBalanceSnapshot, SmsProvider as SmsProviderModel
)
from .serializers import (
    TemplateSerializer, MessageLogSerializer, CampaignSerializer, CampaignListSerializer,
    ReminderSerializer, ReminderListSerializer, MessageSerializer,
    ContactLogSerializer, SmsBalanceSnapshotSerializer, SmsProviderSerializer,
    SendManualMessageSerializer
)
from .providers import get_sms_provider


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated, IsMarketer]


class MessageLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MessageLog.objects.all()
    serializer_class = MessageLogSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        return MessageLog.objects.filter(patient__organization=user.organization)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get SMS balance (mock)"""
        return Response({
            'balance': 10000,
            'currency': 'KZT'
        })
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """Manual send message"""
        phone = request.data.get('phone')
        text = request.data.get('text')
        channel = request.data.get('channel', 'sms')
        
        if not phone or not text:
            return Response({'error': 'Phone and text required'}, status=status.HTTP_400_BAD_REQUEST)
        
        provider = get_sms_provider()
        result = provider.send(sender='CLINIC', phone=phone, body=text)
        
        MessageLog.objects.create(
            channel=channel,
            text=text,
            cost=result.cost,
            status='sent' if result.success else 'failed'
        )
        
        return Response({
            'success': result.success,
            'message_id': result.message_id,
            'cost': float(result.cost),
            'error': result.error
        })


# ==================== Marketing ViewSets ====================


class SmsProviderViewSet(viewsets.ModelViewSet):
    """SMS Provider management"""
    queryset = SmsProviderModel.objects.all()
    serializer_class = SmsProviderSerializer
    permission_classes = [IsAuthenticated, IsMarketer]
    
    def get_queryset(self):
        return SmsProviderModel.objects.filter(organization=self.request.user.organization)


class CampaignViewSet(viewsets.ModelViewSet):
    """Campaign management with full prepare/schedule/export functionality"""
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated, IsMarketer]
    
    def get_queryset(self):
        queryset = Campaign.objects.filter(organization=self.request.user.organization)
        
        # Filters
        status_filter = self.request.query_params.get('status')
        channel = self.request.query_params.get('channel')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if channel:
            queryset = queryset.filter(channel=channel)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def prepare(self, request, pk=None):
        """Prepare campaign - materialize audience and calculate cost"""
        from apps.patients.models import Patient
        from apps.visits.models import Visit
        from apps.services.models import Service
        from .models import CampaignRecipient, CampaignAudience
        from .providers import get_sms_provider
        from django.db.models import Q
        from datetime import datetime
        
        campaign = self.get_object()
        
        # Get or create audience config
        try:
            audience = campaign.audience
            filters = audience.filters
        except:
            return Response(
                {'error': 'Campaign audience not configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build query
        patients_query = Patient.objects.filter(organization=self.request.user.organization)
        
        # Apply filters
        if filters.get('tags'):
            # Filter by tags (contains any)
            patients_query = patients_query.filter(tags__overlap=filters['tags'])
        
        if filters.get('is_opt_in', True):
            patients_query = patients_query.filter(is_marketing_opt_in=True)
        
        if filters.get('services'):
            # Filter by patients who had these services
            service_ids = filters['services']
            visit_patients = Visit.objects.filter(
                services__in=service_ids
            ).values_list('patient_id', flat=True).distinct()
            patients_query = patients_query.filter(id__in=visit_patients)
        
        if filters.get('last_visit_from') or filters.get('last_visit_to'):
            # Filter by last visit date
            visit_query = Visit.objects.filter(patient__in=patients_query)
            if filters.get('last_visit_from'):
                visit_query = visit_query.filter(date__gte=filters['last_visit_from'])
            if filters.get('last_visit_to'):
                visit_query = visit_query.filter(date__lte=filters['last_visit_to'])
            patient_ids = visit_query.values_list('patient_id', flat=True).distinct()
            patients_query = patients_query.filter(id__in=patient_ids)
        
        if filters.get('birthdate_from') or filters.get('birthdate_to'):
            # Filter by birthdate in period (for birthday campaigns)
            if filters.get('birthdate_from'):
                date_from = datetime.strptime(filters['birthdate_from'], '%Y-%m-%d').date()
                patients_query = patients_query.filter(
                    birth_date__month__gte=date_from.month,
                    birth_date__day__gte=date_from.day
                )
            if filters.get('birthdate_to'):
                date_to = datetime.strptime(filters['birthdate_to'], '%Y-%m-%d').date()
                patients_query = patients_query.filter(
                    birth_date__month__lte=date_to.month,
                    birth_date__day__lte=date_to.day
                )
        
        # Get patients
        patients = list(patients_query)
        
        if not patients:
            return Response({
                'total_recipients': 0,
                'estimated_cost': 0,
                'estimated_segments': 0,
                'message': 'No patients match the criteria'
            })
        
        # Calculate cost estimate
        provider = get_sms_provider(self.request.user.organization)
        
        # Get message template
        try:
            template = campaign.message_template
            body = template.body
        except:
            body = 'Test message'  # Fallback
        
        # Detect cyrillic and calculate segments
        is_cyrillic = any('\u0400' <= char <= '\u04FF' for char in body)
        max_chars = 70 if is_cyrillic else 160
        max_chars_multi = 67 if is_cyrillic else 153
        
        if len(body) <= max_chars:
            segments_per_message = 1
        else:
            segments_per_message = (len(body) + max_chars_multi - 1) // max_chars_multi
        
        total_segments = len(patients) * segments_per_message
        estimated_cost = total_segments * provider.price_per_sms
        
        # Clear existing recipients if re-preparing
        CampaignRecipient.objects.filter(campaign=campaign).delete()
        
        # Create recipients
        recipients_created = 0
        for patient in patients:
            if patient.phone:
                CampaignRecipient.objects.create(
                    campaign=campaign,
                    patient=patient,
                    phone=patient.phone,
                    status='pending'
                )
                recipients_created += 1
        
        # Update campaign
        campaign.total_recipients = recipients_created
        campaign.status = 'draft'  # Keep in draft until scheduled
        campaign.save()
        
        return Response({
            'total_recipients': recipients_created,
            'estimated_cost': float(estimated_cost),
            'estimated_segments': total_segments,
            'price_per_sms': float(provider.price_per_sms),
            'segments_per_message': segments_per_message
        })
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule campaign for sending"""
        from django.utils import timezone
        from datetime import datetime
        
        campaign = self.get_object()
        
        # Check if campaign is prepared
        if campaign.total_recipients == 0:
            return Response(
                {'error': 'Campaign not prepared. Run prepare first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get schedule time
        schedule_type = request.data.get('schedule_type', 'now')  # 'now', 'scheduled', 'batch'
        scheduled_at = request.data.get('scheduled_at')  # ISO datetime
        
        if schedule_type == 'now':
            campaign.scheduled_at = timezone.now()
            campaign.status = 'scheduled'
        elif schedule_type == 'scheduled' and scheduled_at:
            try:
                campaign.scheduled_at = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
                campaign.status = 'scheduled'
            except:
                return Response(
                    {'error': 'Invalid scheduled_at format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif schedule_type == 'batch':
            # Batch sending (will be processed by celery task)
            campaign.scheduled_at = timezone.now()
            campaign.status = 'scheduled'
        else:
            return Response(
                {'error': 'Invalid schedule_type or missing scheduled_at'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.save()
        
        # Log audit
        from .models import AuditLog
        AuditLog.objects.create(
            organization=self.request.user.organization,
            user=self.request.user,
            action='send',
            entity_type='campaign',
            entity_id=campaign.id,
            changes={'status': 'scheduled', 'scheduled_at': str(campaign.scheduled_at)},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'id': str(campaign.id),
            'status': campaign.status,
            'scheduled_at': campaign.scheduled_at,
            'total_recipients': campaign.total_recipients
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause running campaign"""
        campaign = self.get_object()
        if campaign.status == 'running':
            campaign.status = 'paused'
            campaign.save()
            
            # Log audit
            from .models import AuditLog
            AuditLog.objects.create(
                organization=self.request.user.organization,
                user=self.request.user,
                action='pause',
                entity_type='campaign',
                entity_id=campaign.id,
                changes={'status': 'paused'},
                ip_address=self.request.META.get('REMOTE_ADDR')
            )
            
            return Response({'status': 'paused'})
        return Response({'error': 'Campaign is not running'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume paused campaign"""
        campaign = self.get_object()
        if campaign.status == 'paused':
            campaign.status = 'running'
            campaign.save()
            
            # Log audit
            from .models import AuditLog
            AuditLog.objects.create(
                organization=self.request.user.organization,
                user=self.request.user,
                action='resume',
                entity_type='campaign',
                entity_id=campaign.id,
                changes={'status': 'running'},
                ip_address=self.request.META.get('REMOTE_ADDR')
            )
            
            return Response({'status': 'running'})
        return Response({'error': 'Campaign is not paused'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def recipients(self, request, pk=None):
        """Get campaign recipients with optional status filter"""
        from .models import CampaignRecipient
        from .serializers import CampaignRecipientSerializer
        
        campaign = self.get_object()
        status_filter = request.query_params.get('status')
        
        recipients = CampaignRecipient.objects.filter(campaign=campaign)
        if status_filter:
            recipients = recipients.filter(status=status_filter)
        
        serializer = CampaignRecipientSerializer(recipients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export campaign results to Excel"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        from django.http import HttpResponse
        from .models import CampaignRecipient
        
        campaign = self.get_object()
        recipients = CampaignRecipient.objects.filter(campaign=campaign).select_related('patient')
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Campaign Results"
        
        # Headers
        headers = ['Patient', 'Phone', 'Status', 'Cost', 'Sent At', 'Delivered At', 'Error']
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Data
        for recipient in recipients:
            ws.append([
                recipient.patient.full_name,
                recipient.phone,
                recipient.get_status_display(),
                float(recipient.cost) if recipient.cost else 0,
                recipient.sent_at.strftime('%Y-%m-%d %H:%M:%S') if recipient.sent_at else '',
                recipient.delivered_at.strftime('%Y-%m-%d %H:%M:%S') if recipient.delivered_at else '',
                recipient.error or ''
            ])
        
        # Summary row
        ws.append([])
        ws.append(['Summary', '', '', '', '', '', ''])
        ws.append(['Total Recipients', campaign.total_recipients])
        ws.append(['Sent', campaign.sent_count])
        ws.append(['Delivered', campaign.delivered_count])
        ws.append(['Failed', campaign.failed_count])
        ws.append(['Total Cost', float(campaign.total_cost)])
        ws.append(['Delivery Rate', f"{campaign.delivered_rate}%"])
        ws.append(['Conversion Rate', f"{campaign.conversion_rate}%"])
        ws.append(['Visits', campaign.visit_count])
        ws.append(['Revenue', float(campaign.visit_amount)])
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=campaign_{campaign.id}_results.xlsx'
        
        wb.save(response)
        return response


class ReminderViewSet(viewsets.ModelViewSet):
    """Reminder management with test/toggle functionality"""
    queryset = Reminder.objects.all()
    permission_classes = [IsAuthenticated, IsMarketer]
    filterset_fields = ['enabled', 'type', 'channel']
    
    def get_queryset(self):
        queryset = Reminder.objects.filter(organization=self.request.user.organization)
        
        # Additional filters
        period_from = self.request.query_params.get('period_from')
        period_to = self.request.query_params.get('period_to')
        
        if period_from:
            queryset = queryset.filter(created_at__gte=period_from)
        if period_to:
            queryset = queryset.filter(created_at__lte=period_to)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReminderListSerializer
        return ReminderSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test reminder by sending test message to specified phone"""
        from .models import Patient
        from .providers import get_sms_provider, MockSMSProvider
        from django.utils import timezone
        
        reminder = self.get_object()
        phone = request.data.get('phone')
        
        if not phone:
            return Response(
                {'error': 'Phone number required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply placeholders with dummy data
        test_body = reminder.body
        placeholders = {
            '_ИМЯ_ПАЦИЕНТА_': 'Иван',
            '_ИМЯ_ОТЧЕСТВО_ПАЦИЕНТА_': 'Иван Иванович',
            '_ДАТА_ВИЗИТА_': timezone.now().strftime('%d.%m.%Y'),
            '_ССЫЛКА_НА_ОНЛАЙН_ЗАПИСЬ_': 'https://clinic.example.com/booking',
        }
        
        for placeholder, value in placeholders.items():
            test_body = test_body.replace(placeholder, value)
        
        # Get provider and send
        provider = get_sms_provider(self.request.user.organization)
        result = provider.send(
            sender=self.request.user.organization.name[:20] if hasattr(self.request.user.organization, 'name') else 'CLINIC',
            phone=phone,
            body=test_body
        )
        
        if result.success:
            return Response({
                'success': True,
                'message_id': result.message_id,
                'segments': result.segments,
                'cost': float(result.cost),
                'body': test_body
            })
        else:
            return Response(
                {'error': result.error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'])
    def toggle(self, request, pk=None):
        """Toggle reminder enabled state"""
        reminder = self.get_object()
        reminder.enabled = not reminder.enabled
        reminder.save()
        
        # Log audit
        from .models import AuditLog
        AuditLog.objects.create(
            organization=self.request.user.organization,
            user=self.request.user,
            action='update',
            entity_type='reminder',
            entity_id=reminder.id,
            changes={'enabled': reminder.enabled},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'id': str(reminder.id),
            'enabled': reminder.enabled
        })


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """Message log (read-only)"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        return Message.objects.filter(organization=self.request.user.organization)
    
    @action(detail=False, methods=['post'])
    def send_manual(self, request):
        """Send manual message - TO BE IMPLEMENTED IN E4"""
        return Response({'message': 'To be implemented in E4'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class ContactLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Contact log (for reports)"""
    queryset = ContactLog.objects.all()
    serializer_class = ContactLogSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        queryset = ContactLog.objects.filter(organization=self.request.user.organization)
        
        # Filters
        patient_id = self.request.query_params.get('patient_id')
        channel = self.request.query_params.get('channel')
        status = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if channel:
            queryset = queryset.filter(channel=channel)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset


class SmsBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """SMS balance reports"""
    queryset = SmsBalanceSnapshot.objects.all()
    serializer_class = SmsBalanceSnapshotSerializer
    permission_classes = [IsAuthenticated, IsMarketer]
    
    def get_queryset(self):
        return SmsBalanceSnapshot.objects.filter(organization=self.request.user.organization)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current period balance - TO BE IMPLEMENTED IN E5"""
        return Response({'message': 'To be implemented in E5'}, status=status.HTTP_501_NOT_IMPLEMENTED)

