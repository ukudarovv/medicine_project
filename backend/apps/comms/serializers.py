from rest_framework import serializers
from .models import (
    Template, MessageLog, SmsProvider, Campaign, CampaignAudience,
    CampaignMessageTemplate, CampaignRecipient, Reminder, ReminderJob,
    Message, SmsBalanceSnapshot, ContactLog, AuditLog
)


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'channel', 'key', 'subject', 'body', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['id', 'patient', 'appointment', 'channel', 'template_key', 'text', 'cost', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


# ==================== Marketing Serializers ====================


class SmsProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsProvider
        fields = [
            'id', 'organization', 'name', 'api_key', 'api_secret', 'sender_name',
            'rate_limit_per_min', 'price_per_sms', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
        }


class CampaignAudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignAudience
        fields = ['id', 'filters']
        read_only_fields = ['id']


class CampaignMessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignMessageTemplate
        fields = ['id', 'body', 'placeholders', 'max_segments']
        read_only_fields = ['id']


class CampaignSerializer(serializers.ModelSerializer):
    audience = CampaignAudienceSerializer(required=False)
    message_template = CampaignMessageTemplateSerializer(required=False)
    delivered_rate = serializers.ReadOnlyField()
    conversion_rate = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'organization', 'title', 'channel', 'sender_name', 'status', 'scheduled_at',
            'total_recipients', 'sent_count', 'delivered_count', 'failed_count',
            'visit_count', 'visit_amount', 'total_cost', 'delivered_rate', 'conversion_rate',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'audience', 'message_template'
        ]
        read_only_fields = [
            'id', 'total_recipients', 'sent_count', 'delivered_count', 'failed_count',
            'visit_count', 'visit_amount', 'total_cost', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        audience_data = validated_data.pop('audience', None)
        template_data = validated_data.pop('message_template', None)
        
        campaign = Campaign.objects.create(**validated_data)
        
        if audience_data:
            CampaignAudience.objects.create(campaign=campaign, **audience_data)
        
        if template_data:
            CampaignMessageTemplate.objects.create(campaign=campaign, **template_data)
        
        return campaign
    
    def update(self, instance, validated_data):
        audience_data = validated_data.pop('audience', None)
        template_data = validated_data.pop('message_template', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if audience_data:
            CampaignAudience.objects.update_or_create(
                campaign=instance,
                defaults=audience_data
            )
        
        if template_data:
            CampaignMessageTemplate.objects.update_or_create(
                campaign=instance,
                defaults=template_data
            )
        
        return instance


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    delivered_rate = serializers.ReadOnlyField()
    conversion_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'channel', 'status', 'scheduled_at',
            'total_recipients', 'sent_count', 'delivered_count',
            'visit_count', 'visit_amount', 'delivered_rate', 'conversion_rate',
            'created_at'
        ]


class CampaignRecipientSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = CampaignRecipient
        fields = [
            'id', 'campaign', 'patient', 'patient_name', 'phone', 'status',
            'provider_msg_id', 'error', 'cost', 'sent_at', 'delivered_at', 'created_at'
        ]
        read_only_fields = ['id', 'provider_msg_id', 'error', 'cost', 'sent_at', 'delivered_at', 'created_at']


class ReminderSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    link_service_name = serializers.CharField(source='link_service.name', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'organization', 'name', 'enabled', 'type', 'type_display',
            'link_service', 'link_service_name', 'offset_days', 'offset_hours',
            'channel', 'channel_display', 'body', 'sent_count', 'delivered_count',
            'visit_count', 'online_bookings_count', 'visit_amount', 'conversion_rate',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sent_count', 'delivered_count', 'visit_count',
            'online_bookings_count', 'visit_amount', 'created_at', 'updated_at'
        ]


class ReminderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    conversion_rate = serializers.ReadOnlyField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'name', 'enabled', 'type', 'type_display', 'channel',
            'sent_count', 'visit_count', 'online_bookings_count',
            'visit_amount', 'conversion_rate', 'created_at'
        ]


class ReminderJobSerializer(serializers.ModelSerializer):
    reminder_name = serializers.CharField(source='reminder.name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = ReminderJob
        fields = [
            'id', 'reminder', 'reminder_name', 'patient', 'patient_name',
            'visit', 'appointment', 'scheduled_at', 'status',
            'provider_msg_id', 'error', 'attempts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider_msg_id', 'error', 'attempts', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'organization', 'patient', 'patient_name', 'channel', 'channel_display',
            'body', 'sender', 'context', 'status', 'status_display', 'cost',
            'provider_msg_id', 'error', 'sent_at', 'delivered_at', 'created_at'
        ]
        read_only_fields = ['id', 'provider_msg_id', 'error', 'sent_at', 'delivered_at', 'created_at']


class SmsBalanceSnapshotSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = SmsBalanceSnapshot
        fields = [
            'id', 'organization', 'provider', 'provider_name',
            'period_from', 'period_to', 'sent', 'delivered', 'failed', 'cost', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContactLogSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ContactLog
        fields = [
            'id', 'organization', 'patient', 'patient_name', 'channel', 'channel_display',
            'body_hash', 'status', 'status_display', 'related_visit', 'amount',
            'message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    entity_type_display = serializers.CharField(source='get_entity_type_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'organization', 'user', 'user_name', 'action', 'action_display',
            'entity_type', 'entity_type_display', 'entity_id', 'changes',
            'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ==================== Utility Serializers ====================


class SendManualMessageSerializer(serializers.Serializer):
    """Serializer for manual message sending"""
    patient_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text='List of patient IDs'
    )
    body = serializers.CharField(required=True, help_text='Message body')
    channel = serializers.ChoiceField(
        choices=['sms', 'whatsapp', 'telegram'],
        default='sms',
        help_text='Communication channel'
    )
    
    def validate_body(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('Message body cannot be empty')
        return value


class CampaignPrepareSerializer(serializers.Serializer):
    """Serializer for campaign preparation (dry-run)"""
    filters = serializers.JSONField(required=True, help_text='Audience filters')
    
    def validate_filters(self, value):
        # Validate filter structure
        allowed_keys = ['tags', 'services', 'last_visit_from', 'last_visit_to', 'birthdate_from', 'birthdate_to', 'is_opt_in']
        for key in value.keys():
            if key not in allowed_keys:
                raise serializers.ValidationError(f'Invalid filter key: {key}')
        return value

