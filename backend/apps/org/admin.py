from django.contrib import admin
from .models import Organization, Branch, Room, Resource, Settings, ClinicInfo


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'sms_sender', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'phone', 'is_active', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['organization', 'is_active', 'created_at']
    raw_id_fields = ['organization']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'color', 'is_active', 'order']
    search_fields = ['name']
    list_filter = ['branch', 'is_active']
    raw_id_fields = ['branch']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'branch', 'room', 'is_active']
    search_fields = ['name']
    list_filter = ['type', 'branch', 'is_active']
    raw_id_fields = ['branch', 'room']


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'organization', 'branch', 'updated_at']
    search_fields = ['key', 'description']
    list_filter = ['organization', 'branch', 'updated_at']
    raw_id_fields = ['organization', 'branch']


@admin.register(ClinicInfo)
class ClinicInfoAdmin(admin.ModelAdmin):
    list_display = ['organization', 'inn', 'kpp', 'license_number', 'updated_at']
    search_fields = ['legal_name', 'inn', 'kpp']
    raw_id_fields = ['organization']
    
    fieldsets = (
        ('Организация', {
            'fields': ('organization',)
        }),
        ('Реквизиты', {
            'fields': ('inn', 'kpp', 'ogrn', 'legal_name', 'legal_address')
        }),
        ('Контакты', {
            'fields': ('website', 'support_email', 'support_phone')
        }),
        ('Лицензия', {
            'fields': ('license_number', 'license_issued_date', 'license_issued_by')
        }),
    )

