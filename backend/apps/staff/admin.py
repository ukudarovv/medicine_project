from django.contrib import admin
from .models import Employee, EmployeeBranch, EmployeeService


class EmployeeBranchInline(admin.TabularInline):
    model = EmployeeBranch
    extra = 1
    raw_id_fields = ['branch']


class EmployeeServiceInline(admin.TabularInline):
    model = EmployeeService
    extra = 1
    raw_id_fields = ['service']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'position', 'phone',
        'is_active', 'hire_date', 'created_at'
    ]
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'iin']
    list_filter = ['organization', 'position', 'is_active', 'hire_date']
    raw_id_fields = ['organization', 'user']
    inlines = [EmployeeBranchInline, EmployeeServiceInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'user', 'first_name', 'last_name', 'middle_name')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Должность', {
            'fields': ('position', 'specialization', 'hire_date', 'fire_date')
        }),
        ('Документы', {
            'fields': ('iin', 'passport_series', 'passport_number', 'passport_issued_by', 'passport_issued_date')
        }),
        ('Финансы', {
            'fields': ('commission_percent', 'salary')
        }),
        ('Настройки', {
            'fields': ('color', 'is_active')
        }),
    )


@admin.register(EmployeeBranch)
class EmployeeBranchAdmin(admin.ModelAdmin):
    list_display = ['employee', 'branch', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'branch__name']
    raw_id_fields = ['employee', 'branch']


@admin.register(EmployeeService)
class EmployeeServiceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'service', 'price_override', 'created_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'service__name']
    raw_id_fields = ['employee', 'service']

