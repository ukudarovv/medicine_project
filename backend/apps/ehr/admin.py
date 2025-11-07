"""
Admin interface for EHR models
"""
from django.contrib import admin
from .models import EHRRecord


@admin.register(EHRRecord)
class EHRRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'organization', 'record_type', 'title', 'version', 
                   'is_external', 'is_deleted', 'created_at']
    list_filter = ['record_type', 'organization', 'is_external', 'is_deleted', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'title', 'author__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'version', 'previous_version']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Record Information', {
            'fields': ('id', 'patient', 'organization', 'author')
        }),
        ('Content', {
            'fields': ('record_type', 'title', 'payload')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Versioning', {
            'fields': ('version', 'previous_version')
        }),
        ('Flags', {
            'fields': ('is_external', 'is_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # Include soft-deleted records in admin
        qs = super().get_queryset(request)
        return qs

