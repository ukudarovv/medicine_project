from django.contrib import admin
from .models import Patient, Representative, PatientFile


class RepresentativeInline(admin.TabularInline):
    model = Representative
    extra = 0


class PatientFileInline(admin.TabularInline):
    model = PatientFile
    extra = 0
    fields = ['file_type', 'title', 'file', 'uploaded_by']
    readonly_fields = ['uploaded_by']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'birth_date', 'phone',
        'balance', 'is_active', 'created_at'
    ]
    search_fields = ['first_name', 'last_name', 'phone', 'iin', 'email']
    list_filter = ['organization', 'sex', 'is_active', 'created_at']
    raw_id_fields = ['organization']
    inlines = [RepresentativeInline, PatientFileInline]
    
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

