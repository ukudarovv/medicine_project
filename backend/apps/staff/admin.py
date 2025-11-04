from django.contrib import admin
from .models import (
    Employee, EmployeeBranch, EmployeeService, Position,
    SalarySchemaTemplate, EmployeeSalarySchema,
    EmployeeTask, EmployeeTaskComment, EmployeeTaskAttachment,
    EmployeeResult, EmployeeResultPosition
)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'hidden_in_schedule_filter', 'created_at']
    search_fields = ['name', 'comment']
    list_filter = ['organization', 'hidden_in_schedule_filter']
    raw_id_fields = ['organization']


@admin.register(SalarySchemaTemplate)
class SalarySchemaTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'organization', 'pct_of_own_sales', 'fixed_salary_enabled',
        'min_rate_enabled', 'created_at'
    ]
    search_fields = ['name']
    list_filter = [
        'organization', 'pct_of_own_sales', 'fixed_salary_enabled',
        'min_rate_enabled'
    ]
    raw_id_fields = ['organization']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'name')
        }),
        ('Комиссии', {
            'fields': (
                'pct_of_own_sales', 'pct_value',
                'direction_bonus_enabled', 'direction_bonus_pct',
                'pct_per_created_visits_enabled', 'pct_per_visit'
            )
        }),
        ('Фиксированная ЗП и минимум', {
            'fields': (
                'fixed_salary_enabled', 'fixed_amount', 'currency',
                'min_rate_enabled', 'min_rate_amount'
            )
        }),
        ('Дополнительные настройки', {
            'fields': (
                'honor_patient_discount_enabled',
                'subscription_services_pct_enabled', 'subscription_pct',
                'calc_from_profit_instead_of_revenue'
            )
        }),
    )


class EmployeeBranchInline(admin.TabularInline):
    model = EmployeeBranch
    extra = 1
    raw_id_fields = ['branch']


class EmployeeServiceInline(admin.TabularInline):
    model = EmployeeService
    extra = 1
    raw_id_fields = ['service']


class EmployeeSalarySchemaInline(admin.TabularInline):
    model = EmployeeSalarySchema
    extra = 1
    raw_id_fields = ['salary_template', 'created_by']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'position', 'phone',
        'employment_status', 'is_active', 'hired_at', 'created_at'
    ]
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'iin']
    list_filter = [
        'organization', 'position', 'employment_status', 'is_active',
        'show_in_schedule', 'can_accept_payments'
    ]
    raw_id_fields = ['organization', 'user', 'position', 'warehouse', 'created_by', 'updated_by']
    inlines = [EmployeeBranchInline, EmployeeServiceInline, EmployeeSalarySchemaInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'user', 'first_name', 'last_name', 'middle_name')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Должность', {
            'fields': (
                'position', 'specialization', 'hired_at', 'fired_at',
                'employment_status'
            )
        }),
        ('Документы', {
            'fields': (
                'iin', 'snils', 'inn',
                'passport_series', 'passport_number', 'passport_issued_by',
                'passport_issued_date', 'power_of_attorney_number',
                'power_of_attorney_date'
            )
        }),
        ('Флаги', {
            'fields': (
                'show_in_schedule', 'can_accept_payments', 'can_be_assistant',
                'limit_goods_sales_today_only'
            )
        }),
        ('Онлайн-запись', {
            'fields': (
                'online_slot_step_minutes', 'min_gap_between_visits_minutes',
                'min_gap_between_days_hours'
            )
        }),
        ('Финансы', {
            'fields': ('markup_percent', 'salary')
        }),
        ('Склад', {
            'fields': ('warehouse', 'warehouse_lock')
        }),
        ('Печать документов', {
            'fields': ('is_chief_accountant', 'is_cashier', 'is_org_head')
        }),
        ('Календарь и доступ', {
            'fields': (
                'calendar_color', 'access_template_id', 'is_user_enabled'
            )
        }),
        ('Дополнительно', {
            'fields': ('description', 'is_active')
        }),
        ('Служебная информация', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


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


@admin.register(EmployeeSalarySchema)
class EmployeeSalarySchemaAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'salary_template', 'starts_at', 'ends_at',
        'is_active', 'created_at'
    ]
    search_fields = ['employee__first_name', 'employee__last_name', 'salary_template__name']
    list_filter = ['is_active', 'starts_at', 'ends_at']
    raw_id_fields = ['employee', 'salary_template', 'created_by']


@admin.register(EmployeeResult)
class EmployeeResultAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'created_at']
    search_fields = ['name', 'comment']
    list_filter = ['organization', 'created_at']
    raw_id_fields = ['organization']


class EmployeeTaskCommentInline(admin.TabularInline):
    model = EmployeeTaskComment
    extra = 1
    raw_id_fields = ['author']


class EmployeeTaskAttachmentInline(admin.TabularInline):
    model = EmployeeTaskAttachment
    extra = 1
    raw_id_fields = ['uploaded_by']


@admin.register(EmployeeTask)
class EmployeeTaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'assignee', 'author', 'status', 'deadline_at',
        'result', 'created_at'
    ]
    search_fields = ['title', 'description', 'assignee__first_name', 'assignee__last_name']
    list_filter = ['organization', 'status', 'deadline_at', 'created_at']
    raw_id_fields = ['organization', 'assignee', 'author', 'result']
    inlines = [EmployeeTaskCommentInline, EmployeeTaskAttachmentInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'title', 'description')
        }),
        ('Назначение', {
            'fields': ('assignee', 'author')
        }),
        ('Статус и результат', {
            'fields': ('status', 'result')
        }),
        ('Сроки', {
            'fields': ('deadline_at', 'completed_at')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmployeeTaskComment)
class EmployeeTaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'comment', 'created_at']
    search_fields = ['comment', 'task__title']
    list_filter = ['created_at']
    raw_id_fields = ['task', 'author']


@admin.register(EmployeeTaskAttachment)
class EmployeeTaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'filename', 'uploaded_by', 'created_at']
    search_fields = ['filename', 'task__title']
    list_filter = ['created_at']
    raw_id_fields = ['task', 'uploaded_by']
