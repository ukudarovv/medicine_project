"""
Admin interface for consent system models
"""
from django.contrib import admin
from .models import AccessRequest, ConsentToken, AccessGrant, AuditLog


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'requester_org', 'requester_user', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'delivery_channel', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'requester_org__name', 'requester_user__username']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('id', 'patient', 'requester_org', 'requester_user', 'reason')
        }),
        ('Access Details', {
            'fields': ('scopes', 'requested_duration_days')
        }),
        ('Status', {
            'fields': ('status', 'delivery_channel', 'created_at', 'expires_at', 'responded_at')
        }),
    )


@admin.register(ConsentToken)
class ConsentTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'access_request', 'attempts_count', 'max_attempts', 'created_at', 'used_at']
    list_filter = ['created_at', 'used_at']
    readonly_fields = ['id', 'otp_code_hash', 'created_at', 'used_at']
    search_fields = ['access_request__patient__first_name', 'access_request__patient__last_name']


@admin.register(AccessGrant)
class AccessGrantAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'grantee_org', 'valid_from', 'valid_to', 'is_active_display', 'revoked_at']
    list_filter = ['is_whitelist', 'created_by', 'valid_to', 'revoked_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'grantee_org__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_accessed_at', 'access_count']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Grant Information', {
            'fields': ('id', 'patient', 'grantee_org', 'access_request')
        }),
        ('Access Details', {
            'fields': ('scopes', 'valid_from', 'valid_to', 'is_whitelist', 'created_by')
        }),
        ('Usage Tracking', {
            'fields': ('last_accessed_at', 'access_count')
        }),
        ('Revocation', {
            'fields': ('revoked_at', 'revoked_by', 'revocation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        return obj.is_active()
    is_active_display.boolean = True
    is_active_display.short_description = 'Active'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'user', 'organization', 'action', 'object_type', 'created_at']
    list_filter = ['action', 'object_type', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'user__username', 'organization__name']
    readonly_fields = ['id', 'user', 'organization', 'patient', 'action', 'object_type', 'object_id', 
                      'access_grant', 'ip_address', 'user_agent', 'details', 'created_at']
    date_hierarchy = 'created_at'
    
    # Make audit logs read-only in admin
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

