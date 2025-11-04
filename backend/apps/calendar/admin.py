from django.contrib import admin
from .models import Availability, Appointment, AppointmentResource


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['employee', 'weekday', 'time_from', 'time_to', 'room', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name']
    list_filter = ['weekday', 'is_active']
    raw_id_fields = ['employee', 'room']


class AppointmentResourceInline(admin.TabularInline):
    model = AppointmentResource
    extra = 0
    raw_id_fields = ['resource']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'employee', 'branch', 'start_datetime',
        'end_datetime', 'status', 'is_primary'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'employee__first_name', 'employee__last_name'
    ]
    list_filter = ['branch', 'status', 'is_primary', 'is_urgent', 'start_datetime']
    raw_id_fields = ['branch', 'employee', 'patient', 'room', 'created_by']
    inlines = [AppointmentResourceInline]
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('branch', 'employee', 'patient', 'room')
        }),
        ('Время', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Статус', {
            'fields': ('status', 'is_primary', 'is_urgent')
        }),
        ('Примечания', {
            'fields': ('note', 'cancellation_reason')
        }),
        ('Мета', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AppointmentResource)
class AppointmentResourceAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'resource', 'created_at']
    search_fields = ['resource__name']
    raw_id_fields = ['appointment', 'resource']

