from django.contrib import admin
from .models import (
    Patient, Representative, PatientFile,
    PatientPhone, PatientSocialNetwork, PatientContactPerson,
    PatientDisease, PatientDiagnosis, PatientDoseLoad
)


class RepresentativeInline(admin.TabularInline):
    model = Representative
    extra = 0


class PatientFileInline(admin.TabularInline):
    model = PatientFile
    extra = 0
    fields = ['file_type', 'title', 'file', 'uploaded_by']
    readonly_fields = ['uploaded_by']


class PatientPhoneInline(admin.TabularInline):
    model = PatientPhone
    extra = 0


class PatientDiseaseInline(admin.TabularInline):
    model = PatientDisease
    extra = 0
    raw_id_fields = ['icd_code', 'doctor']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'birth_date', 'phone',
        'balance', 'is_active', 'created_at'
    ]
    search_fields = ['first_name', 'last_name', 'phone', 'iin', 'email']
    list_filter = ['organization', 'sex', 'is_active', 'created_at']
    raw_id_fields = ['organization']
    inlines = [RepresentativeInline, PatientFileInline, PatientPhoneInline, PatientDiseaseInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'first_name', 'last_name', 'middle_name', 'birth_date', 'sex')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Документы', {
            'fields': ('iin', 'documents')
        }),
        ('Согласия', {
            'fields': ('consents',),
            'classes': ('collapse',)
        }),
        ('Финансы', {
            'fields': ('balance', 'discount_percent')
        }),
        ('Медицинская информация', {
            'fields': ('allergies', 'medical_history', 'notes'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'relation', 'patient', 'phone']
    search_fields = ['first_name', 'last_name', 'phone', 'patient__first_name', 'patient__last_name']
    list_filter = ['relation']
    raw_id_fields = ['patient']


@admin.register(PatientFile)
class PatientFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'file_type', 'uploaded_by', 'created_at']
    search_fields = ['title', 'description', 'patient__first_name', 'patient__last_name']
    list_filter = ['file_type', 'created_at']
    raw_id_fields = ['patient', 'uploaded_by']


@admin.register(PatientPhone)
class PatientPhoneAdmin(admin.ModelAdmin):
    list_display = ['patient', 'phone', 'phone_type', 'is_primary']
    list_filter = ['phone_type', 'is_primary']
    raw_id_fields = ['patient']


@admin.register(PatientSocialNetwork)
class PatientSocialNetworkAdmin(admin.ModelAdmin):
    list_display = ['patient', 'network', 'username']
    list_filter = ['network']
    raw_id_fields = ['patient']


@admin.register(PatientContactPerson)
class PatientContactPersonAdmin(admin.ModelAdmin):
    list_display = ['patient', 'name', 'relation', 'phone']
    raw_id_fields = ['patient']


@admin.register(PatientDisease)
class PatientDiseaseAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diagnosis', 'icd_code', 'start_date', 'doctor']
    list_filter = ['start_date']
    raw_id_fields = ['patient', 'icd_code', 'doctor']


@admin.register(PatientDiagnosis)
class PatientDiagnosisAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diagnosis', 'icd_code', 'date', 'is_primary', 'doctor']
    list_filter = ['date', 'is_primary']
    raw_id_fields = ['patient', 'icd_code', 'doctor']


@admin.register(PatientDoseLoad)
class PatientDoseLoadAdmin(admin.ModelAdmin):
    list_display = ['patient', 'study_type', 'dose', 'date']
    list_filter = ['date']
    raw_id_fields = ['patient']
