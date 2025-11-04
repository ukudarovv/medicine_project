from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsMarketer
from .models import Template, MessageLog
from .serializers import TemplateSerializer, MessageLogSerializer
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
        result = provider.send_sms(phone, text)
        
        MessageLog.objects.create(
            channel=channel,
            text=text,
            cost=result.get('cost', 0),
            status='sent' if result.get('success') else 'failed'
        )
        
        return Response(result)

