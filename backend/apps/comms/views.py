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
    """Campaign management (will be extended in E3)"""
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated, IsMarketer]
    
    def get_queryset(self):
        return Campaign.objects.filter(organization=self.request.user.organization)
    
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
        """Prepare campaign (materialize audience) - TO BE IMPLEMENTED"""
        return Response({'message': 'To be implemented in E3'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule campaign - TO BE IMPLEMENTED"""
        return Response({'message': 'To be implemented in E3'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause campaign"""
        campaign = self.get_object()
        if campaign.status == 'running':
            campaign.status = 'paused'
            campaign.save()
            return Response({'status': 'paused'})
        return Response({'error': 'Campaign is not running'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume campaign"""
        campaign = self.get_object()
        if campaign.status == 'paused':
            campaign.status = 'running'
            campaign.save()
            return Response({'status': 'running'})
        return Response({'error': 'Campaign is not paused'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export campaign results - TO BE IMPLEMENTED"""
        return Response({'message': 'To be implemented in E3'}, status=status.HTTP_501_NOT_IMPLEMENTED)


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

