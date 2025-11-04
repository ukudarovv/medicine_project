from django.contrib import admin
from .models import Template, MessageLog


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['key', 'channel', 'subject', 'created_at']
    list_filter = ['channel']


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['patient', 'channel', 'status', 'cost', 'created_at']
    list_filter = ['channel', 'status', 'created_at']
    raw_id_fields = ['patient', 'appointment']

