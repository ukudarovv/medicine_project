"""
Django Admin for Telegram Bot
"""
from django.contrib import admin
from .models import (
    PatientTelegramLink,
    BotBroadcast,
    BotDocument,
    BotAudit,
    BotFeedback,
    SupportTicket
)


@admin.register(PatientTelegramLink)
class PatientTelegramLinkAdmin(admin.ModelAdmin):
    list_display = ['patient', 'telegram_user_id', 'telegram_username', 'language', 'is_active', 'last_interaction_at']
    list_filter = ['language', 'is_active', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'telegram_username', 'telegram_user_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['patient']


@admin.register(BotBroadcast)
class BotBroadcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'status', 'total_recipients', 'sent_count', 'delivered_count', 'scheduled_at']
    list_filter = ['status', 'organization', 'created_at']
    search_fields = ['title', 'text_ru', 'text_kk']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    raw_id_fields = ['organization', 'created_by']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'organization', 'status', 'created_by')
        }),
        ('Сегментация', {
            'fields': ('segment_filters_json',)
        }),
        ('Сообщения', {
            'fields': ('text_ru', 'text_kk')
        }),
        ('Планирование', {
            'fields': ('scheduled_at', 'started_at', 'completed_at')
        }),
        ('Статистика', {
            'fields': ('total_recipients', 'sent_count', 'delivered_count', 'failed_count', 'clicked_count')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BotDocument)
class BotDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'document_type', 'language', 'expires_at', 'is_expired']
    list_filter = ['document_type', 'language', 'is_expired', 'created_at']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['patient', 'related_visit']


@admin.register(BotAudit)
class BotAuditAdmin(admin.ModelAdmin):
    list_display = ['patient_telegram_link', 'action', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['patient_telegram_link__patient__first_name', 'patient_telegram_link__patient__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['patient_telegram_link']


@admin.register(BotFeedback)
class BotFeedbackAdmin(admin.ModelAdmin):
    list_display = ['patient_telegram_link', 'appointment', 'score', 'is_low_score', 'is_reviewed', 'created_at']
    list_filter = ['score', 'is_low_score', 'is_reviewed', 'created_at']
    search_fields = ['patient_telegram_link__patient__first_name', 'patient_telegram_link__patient__last_name', 'comment']
    readonly_fields = ['created_at', 'is_low_score']
    raw_id_fields = ['appointment', 'patient_telegram_link']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Highlight low scores that need review
        return qs.select_related('patient_telegram_link__patient', 'appointment')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'patient_telegram_link', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'message', 'patient_telegram_link__patient__first_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['patient_telegram_link', 'assigned_to']
    
    fieldsets = (
        ('Обращение', {
            'fields': ('patient_telegram_link', 'subject', 'message')
        }),
        ('Обработка', {
            'fields': ('status', 'assigned_to', 'resolved_at')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at')
        }),
    )

