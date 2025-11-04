from django.contrib import admin
from .models import (
    Template, MessageLog, SmsProvider, Campaign, CampaignRecipient,
    Reminder, ReminderJob, Message, ContactLog, AuditLog
)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['key', 'channel', 'subject', 'created_at']
    list_filter = ['channel']


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['patient', 'channel', 'status', 'cost', 'created_at']
    list_filter = ['channel', 'status', 'created_at']
    raw_id_fields = ['patient', 'appointment']


@admin.register(SmsProvider)
class SmsProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'sender_name', 'rate_limit_per_min', 'price_per_sms', 'is_active']
    list_filter = ['is_active', 'organization']
    search_fields = ['name', 'sender_name']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'channel', 'status', 'total_recipients', 'sent_count', 'delivered_count', 'conversion_rate', 'created_at']
    list_filter = ['status', 'channel', 'organization', 'created_at']
    search_fields = ['title']
    raw_id_fields = ['created_by']
    readonly_fields = ['total_recipients', 'sent_count', 'delivered_count', 'failed_count', 'visit_count', 'visit_amount', 'total_cost']


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ['patient', 'campaign', 'phone', 'status', 'cost', 'sent_at', 'delivered_at']
    list_filter = ['status', 'campaign', 'created_at']
    search_fields = ['phone', 'patient__first_name', 'patient__last_name']
    raw_id_fields = ['campaign', 'patient']


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'type', 'enabled', 'channel', 'sent_count', 'conversion_rate', 'created_at']
    list_filter = ['enabled', 'type', 'channel', 'organization']
    search_fields = ['name']
    raw_id_fields = ['link_service', 'created_by']
    readonly_fields = ['sent_count', 'delivered_count', 'visit_count', 'online_bookings_count', 'visit_amount']


@admin.register(ReminderJob)
class ReminderJobAdmin(admin.ModelAdmin):
    list_display = ['reminder', 'patient', 'scheduled_at', 'status', 'attempts', 'created_at']
    list_filter = ['status', 'reminder', 'scheduled_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'reminder__name']
    raw_id_fields = ['reminder', 'patient', 'visit', 'appointment']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['patient', 'channel', 'status', 'cost', 'sent_at', 'delivered_at', 'created_at']
    list_filter = ['status', 'channel', 'organization', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'body']
    raw_id_fields = ['organization', 'patient']


@admin.register(ContactLog)
class ContactLogAdmin(admin.ModelAdmin):
    list_display = ['patient', 'channel', 'status', 'related_visit', 'amount', 'created_at']
    list_filter = ['status', 'channel', 'organization', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name']
    raw_id_fields = ['organization', 'patient', 'related_visit', 'message']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity_type', 'entity_id', 'ip_address', 'created_at']
    list_filter = ['action', 'entity_type', 'organization', 'created_at']
    search_fields = ['user__email', 'entity_id']
    raw_id_fields = ['organization', 'user']
    readonly_fields = ['action', 'entity_type', 'entity_id', 'changes', 'ip_address', 'created_at']

