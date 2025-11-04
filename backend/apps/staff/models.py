from django.db import models
from django.core.exceptions import ValidationError
from apps.org.models import Organization, Branch
from apps.core.models import User


class Position(models.Model):
    """
    Employee position (Должность)
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    name = models.CharField(max_length=200, help_text='Название должности')
    comment = models.TextField(blank=True, help_text='Комментарий')
    hidden_in_schedule_filter = models.BooleanField(
        default=False,
        help_text='Скрыть из фильтра в расписании'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'positions'
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['name']
        unique_together = ['organization', 'name']
    
    def __str__(self):
        return self.name


class SalarySchemaTemplate(models.Model):
    """
    Salary calculation schema template (Шаблон расчёта ЗП)
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='salary_templates'
    )
    name = models.CharField(max_length=200, help_text='Название шаблона')
    
    # Commission from own sales
    pct_of_own_sales = models.BooleanField(
        default=False,
        help_text='Процент от собственных продаж'
    )
    pct_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Значение процента'
    )
    
    # Direction bonus
    direction_bonus_enabled = models.BooleanField(
        default=False,
        help_text='Бонус за направление'
    )
    direction_bonus_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Процент бонуса за направление'
    )
    
    # Percentage per created visits
    pct_per_created_visits_enabled = models.BooleanField(
        default=False,
        help_text='Процент за созданные визиты'
    )
    pct_per_visit = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Процент за визит'
    )
    
    # Fixed salary
    fixed_salary_enabled = models.BooleanField(
        default=False,
        help_text='Фиксированный оклад'
    )
    fixed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Сумма оклада'
    )
    currency = models.CharField(
        max_length=3,
        default='KZT',
        help_text='Валюта'
    )
    
    # Minimum rate
    min_rate_enabled = models.BooleanField(
        default=False,
        help_text='Минимальная ставка'
    )
    min_rate_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Минимальная сумма'
    )
    
    # Additional settings
    honor_patient_discount_enabled = models.BooleanField(
        default=False,
        help_text='Учитывать скидку пациенту'
    )
    subscription_services_pct_enabled = models.BooleanField(
        default=False,
        help_text='Процент от услуг по абонементам'
    )
    subscription_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Процент от абонементов'
    )
    calc_from_profit_instead_of_revenue = models.BooleanField(
        default=False,
        help_text='Расчёт от прибыли вместо выручки'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'salary_schema_templates'
        verbose_name = 'Salary Schema Template'
        verbose_name_plural = 'Salary Schema Templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Employee model - staff members (doctors, nurses, etc.)
    Extended with HR functionality
    """
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Активен'),
        ('fired', 'Уволен'),
        ('on_leave', 'В отпуске'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile'
    )
    
    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Employment info  
    position_legacy = models.CharField(
        max_length=200,
        blank=True,
        help_text='Должность (legacy field for migration)'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='employees',
        help_text='Должность'
    )
    specialization = models.CharField(max_length=200, blank=True, help_text='Специализация')
    
    # Employment dates and status
    hired_at = models.DateField(null=True, blank=True, help_text='Дата приёма')
    fired_at = models.DateField(null=True, blank=True, help_text='Дата увольнения')
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active',
        help_text='Статус трудоустройства'
    )
    
    # Legacy fields (for backward compatibility)
    hire_date = models.DateField(null=True, blank=True, help_text='Дата приёма (legacy)')
    fire_date = models.DateField(null=True, blank=True, help_text='Дата увольнения (legacy)')
    
    # Identity documents
    iin = models.CharField(max_length=20, blank=True, help_text='ИИН')
    snils = models.CharField(max_length=20, blank=True, help_text='СНИЛС')
    inn = models.CharField(max_length=20, blank=True, help_text='ИНН')
    passport_series = models.CharField(max_length=20, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    passport_issued_by = models.CharField(max_length=500, blank=True)
    passport_issued_date = models.DateField(null=True, blank=True)
    power_of_attorney_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Номер доверенности'
    )
    power_of_attorney_date = models.DateField(
        null=True,
        blank=True,
        help_text='Дата доверенности'
    )
    
    # Flags
    show_in_schedule = models.BooleanField(
        default=True,
        help_text='Показывать в расписании'
    )
    can_accept_payments = models.BooleanField(
        default=False,
        help_text='Может принимать оплату'
    )
    can_be_assistant = models.BooleanField(
        default=False,
        help_text='Может быть ассистентом'
    )
    limit_goods_sales_today_only = models.BooleanField(
        default=False,
        help_text='Финансы только за текущий день'
    )
    
    # Online booking settings
    online_slot_step_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text='Индивидуальный шаг онлайн-записи (минуты)'
    )
    min_gap_between_visits_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text='Минимальный перерыв между визитами (минуты)'
    )
    min_gap_between_days_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text='Минимальный перерыв между днями (часы)'
    )
    
    # Financial settings
    markup_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Персональная наценка на услуги (%)'
    )
    commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Процент комиссии (legacy)'
    )
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Оклад'
    )
    
    # Warehouse settings
    warehouse = models.ForeignKey(
        'warehouse.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_employees',
        help_text='Закреплённый склад'
    )
    warehouse_lock = models.BooleanField(
        default=False,
        help_text='Закрепить за сотрудником склад'
    )
    
    # Document printing flags
    is_chief_accountant = models.BooleanField(
        default=False,
        help_text='Главный бухгалтер'
    )
    is_cashier = models.BooleanField(
        default=False,
        help_text='Кассир'
    )
    is_org_head = models.BooleanField(
        default=False,
        help_text='Руководитель организации'
    )
    
    # Calendar settings
    calendar_color = models.CharField(
        max_length=7,
        default='#2196F3',
        help_text='Цвет в календаре (hex)'
    )
    color = models.CharField(
        max_length=7,
        default='#2196F3',
        help_text='Цвет в календаре (legacy)'
    )
    
    # Access management
    access_template_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID шаблона прав доступа'
    )
    is_user_enabled = models.BooleanField(
        default=False,
        help_text='Разрешить доступ к системе'
    )
    
    # Additional info
    description = models.TextField(blank=True, help_text='Описание')
    
    # Meta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_employees'
    )
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['organization', 'employment_status']),
            models.Index(fields=['organization', 'position']),
        ]
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    def clean(self):
        if self.hired_at and self.fired_at and self.hired_at >= self.fired_at:
            raise ValidationError('Дата приёма должна быть раньше даты увольнения')
        
        if self.online_slot_step_minutes and self.online_slot_step_minutes not in [5, 10, 15, 20, 30, 60]:
            raise ValidationError('Шаг слота должен быть одним из: 5, 10, 15, 20, 30, 60 минут')
        
        if self.min_gap_between_visits_minutes and self.min_gap_between_visits_minutes < 0:
            raise ValidationError('Перерыв между визитами не может быть отрицательным')


class EmployeeSalarySchema(models.Model):
    """
    Employee to Salary Schema Template binding (История назначений схем ЗП)
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_schemas'
    )
    salary_template = models.ForeignKey(
        SalarySchemaTemplate,
        on_delete=models.CASCADE,
        related_name='employee_assignments'
    )
    starts_at = models.DateField(help_text='Дата начала действия')
    ends_at = models.DateField(
        null=True,
        blank=True,
        help_text='Дата окончания действия'
    )
    is_active = models.BooleanField(default=True, help_text='Активна')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_salary_schemas'
    )
    
    class Meta:
        db_table = 'employee_salary_schemas'
        verbose_name = 'Employee Salary Schema'
        verbose_name_plural = 'Employee Salary Schemas'
        ordering = ['-starts_at']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.salary_template.name}"
    
    def clean(self):
        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValidationError('Дата начала должна быть раньше даты окончания')


class EmployeeResult(models.Model):
    """
    Task results reference (Справочник результатов задач)
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='task_results'
    )
    name = models.CharField(max_length=200, help_text='Название результата')
    comment = models.TextField(blank=True, help_text='Комментарий')
    
    # Many-to-many with positions
    positions = models.ManyToManyField(
        Position,
        through='EmployeeResultPosition',
        related_name='task_results',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employee_results'
        verbose_name = 'Employee Result'
        verbose_name_plural = 'Employee Results'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EmployeeResultPosition(models.Model):
    """
    Many-to-many relationship between Results and Positions
    """
    result = models.ForeignKey(
        EmployeeResult,
        on_delete=models.CASCADE
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE
    )
    
    class Meta:
        db_table = 'employee_result_positions'
        unique_together = ['result', 'position']
        verbose_name = 'Result Position Assignment'
        verbose_name_plural = 'Result Position Assignments'


class EmployeeTask(models.Model):
    """
    Task assigned to employee (Задачи сотрудникам)
    """
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В процессе'),
        ('done', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employee_tasks'
    )
    title = models.CharField(max_length=500, help_text='Название задачи')
    description = models.TextField(blank=True, help_text='Описание')
    
    # Assignment
    assignee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        help_text='Исполнитель'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        help_text='Автор'
    )
    
    # Status and result
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text='Статус'
    )
    result = models.ForeignKey(
        EmployeeResult,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        help_text='Результат'
    )
    
    # Timing
    deadline_at = models.DateTimeField(help_text='Дедлайн')
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Дата завершения'
    )
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employee_tasks'
        verbose_name = 'Employee Task'
        verbose_name_plural = 'Employee Tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'assignee', 'status']),
            models.Index(fields=['organization', 'deadline_at']),
            models.Index(fields=['status', 'deadline_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assignee.full_name}"


class EmployeeTaskComment(models.Model):
    """
    Comments on employee tasks
    """
    task = models.ForeignKey(
        EmployeeTask,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_comments'
    )
    comment = models.TextField(help_text='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'employee_task_comments'
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.task.title}"


class EmployeeTaskAttachment(models.Model):
    """
    File attachments for employee tasks
    """
    task = models.ForeignKey(
        EmployeeTask,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(
        upload_to='task_attachments/%Y/%m/%d/',
        help_text='Файл'
    )
    filename = models.CharField(max_length=255, help_text='Имя файла')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_task_files'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'employee_task_attachments'
        verbose_name = 'Task Attachment'
        verbose_name_plural = 'Task Attachments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.filename} - {self.task.title}"


class EmployeeBranch(models.Model):
    """
    Many-to-many relationship between employees and branches
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='branch_assignments'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='employee_assignments'
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'employee_branches'
        unique_together = ['employee', 'branch']
        verbose_name = 'Employee Branch Assignment'
        verbose_name_plural = 'Employee Branch Assignments'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.branch.name}"


class EmployeeService(models.Model):
    """
    Services that an employee can provide with custom pricing
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='service_assignments'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='employee_assignments'
    )
    price_override = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Индивидуальная цена (если отличается от стандартной)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'employee_services'
        unique_together = ['employee', 'service']
        verbose_name = 'Employee Service'
        verbose_name_plural = 'Employee Services'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.service.name}"
