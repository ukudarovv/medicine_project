from django.contrib import admin
from .models import Visit, VisitService, VisitPrescription, VisitResource


class VisitServiceInline(admin.TabularInline):
    model = VisitService
    extra = 0
    raw_id_fields = ['service', 'icd']


class VisitPrescriptionInline(admin.StackedInline):
    model = VisitPrescription
    extra = 0


class VisitResourceInline(admin.TabularInline):
    model = VisitResource
    extra = 0
    raw_id_fields = ['resource']


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'status', 'is_patient_arrived', 'created_at']
    list_filter = ['status', 'is_patient_arrived', 'created_at']
    search_fields = ['appointment__patient__first_name', 'appointment__patient__last_name']
    raw_id_fields = ['appointment', 'created_by']
    inlines = [VisitServiceInline, VisitPrescriptionInline, VisitResourceInline]


@admin.register(VisitService)
class VisitServiceAdmin(admin.ModelAdmin):
    list_display = ['visit', 'service', 'qty', 'price', 'total_price']
    raw_id_fields = ['visit', 'service', 'icd']


@admin.register(VisitPrescription)
class VisitPrescriptionAdmin(admin.ModelAdmin):
    list_display = ['visit', 'medication', 'dosage', 'duration_days']
    raw_id_fields = ['visit']


@admin.register(VisitResource)
class VisitResourceAdmin(admin.ModelAdmin):
    list_display = ['visit', 'resource', 'used_time']
    raw_id_fields = ['visit', 'resource']

