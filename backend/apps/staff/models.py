from django.db import models
from apps.org.models import Organization, Branch
from apps.core.models import User


class Employee(models.Model):
    """
    Employee model - staff members (doctors, nurses, etc.)
    """
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
    position = models.CharField(max_length=200, help_text='Должность')
    specialization = models.CharField(max_length=200, blank=True, help_text='Специализация')
    hire_date = models.DateField(help_text='Дата приёма')
    fire_date = models.DateField(null=True, blank=True, help_text='Дата увольнения')
    
    # Identity documents
    iin = models.CharField(max_length=20, blank=True, help_text='ИИН')
    passport_series = models.CharField(max_length=20, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    passport_issued_by = models.CharField(max_length=500, blank=True)
    passport_issued_date = models.DateField(null=True, blank=True)
    
    # Финансы
    commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Процент комиссии'
    )
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Оклад'
    )
    
    # Calendar settings
    color = models.CharField(
        max_length=7,
        default='#2196F3',
        help_text='Цвет в календаре (hex)'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


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

