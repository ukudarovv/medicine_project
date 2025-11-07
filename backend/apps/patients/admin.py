from django.contrib import admin
from .models import (
    Patient, Representative, PatientFile,
    PatientPhone, PatientSocialNetwork, PatientContactPerson,
    PatientDisease, PatientDiagnosis, PatientDoseLoad, ConsentHistory,
    MedicalExamination, MedExamPastDisease, MedExamVaccination, MedExamLabTest,
    TreatmentPlan, TreatmentStage, TreatmentStageItem, TreatmentPlanTemplate
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
        'get_organizations_list', 'balance', 'is_active', 'created_at'
    ]
    search_fields = ['first_name', 'last_name', 'phone', 'iin', 'email']
    list_filter = ['sex', 'is_active', 'created_at']
    filter_horizontal = ['organizations']
    inlines = [RepresentativeInline, PatientFileInline, PatientPhoneInline, PatientDiseaseInline]
    
    def get_organizations_list(self, obj):
        """Display list of organizations for the patient"""
        orgs = obj.organizations.all()
        if orgs:
            return ', '.join([org.name for org in orgs])
        return '-'
    get_organizations_list.short_description = 'Организации'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organizations', 'first_name', 'last_name', 'middle_name', 'birth_date', 'sex')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address', 'kato_address')
        }),
        ('Документы', {
            'fields': ('iin', 'iin_verified', 'iin_verified_at', 'documents')
        }),
        ('ОСМС (КZ)', {
            'fields': ('osms_status', 'osms_category', 'osms_verified_at'),
            'classes': ('collapse',)
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
    list_display = ['patient', 'phone', 'type', 'is_primary']
    list_filter = ['type', 'is_primary']
    raw_id_fields = ['patient']


@admin.register(PatientSocialNetwork)
class PatientSocialNetworkAdmin(admin.ModelAdmin):
    list_display = ['patient', 'network', 'username']
    list_filter = ['network']
    raw_id_fields = ['patient']


@admin.register(PatientContactPerson)
class PatientContactPersonAdmin(admin.ModelAdmin):
    list_display = ['patient', 'first_name', 'last_name', 'relation', 'phone']
    raw_id_fields = ['patient']


@admin.register(PatientDisease)
class PatientDiseaseAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diagnosis', 'icd_code', 'start_date', 'doctor']
    list_filter = ['start_date']
    raw_id_fields = ['patient', 'icd_code', 'doctor']


@admin.register(PatientDiagnosis)
class PatientDiagnosisAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diagnosis', 'icd_code', 'date', 'type', 'doctor']
    list_filter = ['date', 'type']
    raw_id_fields = ['patient', 'icd_code', 'doctor']


@admin.register(PatientDoseLoad)
class PatientDoseLoadAdmin(admin.ModelAdmin):
    list_display = ['patient', 'study_type', 'dose', 'date']
    list_filter = ['date']
    raw_id_fields = ['patient']


@admin.register(ConsentHistory)
class ConsentHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'consent_type', 'status', 'accepted_by', 'ip_address', 'created_at']
    list_filter = ['consent_type', 'status', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'ip_address']
    raw_id_fields = ['patient', 'accepted_by']
    readonly_fields = ['created_at']


# ==================== Sprint 3: Medical Examinations ====================


class MedExamPastDiseaseInline(admin.TabularInline):
    model = MedExamPastDisease
    extra = 0
    raw_id_fields = ['icd_code']


class MedExamVaccinationInline(admin.TabularInline):
    model = MedExamVaccination
    extra = 0


class MedExamLabTestInline(admin.TabularInline):
    model = MedExamLabTest
    extra = 0
    raw_id_fields = ['file']


@admin.register(MedicalExamination)
class MedicalExaminationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'exam_type', 'exam_date', 'fit_for_work', 'next_exam_date']
    list_filter = ['exam_type', 'exam_date', 'fit_for_work']
    search_fields = ['patient__first_name', 'patient__last_name', 'work_profile']
    raw_id_fields = ['patient', 'created_by']
    inlines = [MedExamPastDiseaseInline, MedExamVaccinationInline, MedExamLabTestInline]


# ==================== Sprint 3: Treatment Plans ====================


class TreatmentStageInline(admin.TabularInline):
    model = TreatmentStage
    extra = 0
    fields = ['order', 'title', 'status', 'start_date', 'end_date']


@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'title', 'status', 'start_date', 'total_cost', 'total_cost_frozen']
    list_filter = ['status', 'total_cost_frozen', 'start_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'title']
    raw_id_fields = ['patient', 'created_by']
    inlines = [TreatmentStageInline]


class TreatmentStageItemInline(admin.TabularInline):
    model = TreatmentStageItem
    extra = 0
    raw_id_fields = ['service']


@admin.register(TreatmentStage)
class TreatmentStageAdmin(admin.ModelAdmin):
    list_display = ['plan', 'order', 'title', 'status', 'start_date']
    list_filter = ['status']
    raw_id_fields = ['plan']
    inlines = [TreatmentStageItemInline]


@admin.register(TreatmentPlanTemplate)
class TreatmentPlanTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['organization', 'created_by']
