from django.db import models


class Organization(models.Model):
    """
    Organization model - top level entity for multi-tenancy
    """
    name = models.CharField(max_length=200)
    sms_sender = models.CharField(max_length=50, blank=True, help_text='SMS sender name')
    logo = models.ImageField(upload_to='organization/logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name


class Branch(models.Model):
    """
    Branch/Clinic model - each organization can have multiple branches
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='branches'
    )
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Almaty')
    work_hours_from = models.TimeField(default='09:00')
    work_hours_to = models.TimeField(default='20:00')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'branches'
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Room(models.Model):
    """
    Room/Cabinet model - rooms within a branch
    """
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#2196F3', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rooms'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class Resource(models.Model):
    """
    Resource model - equipment, chairs, etc.
    """
    RESOURCE_TYPES = [
        ('chair', 'Dental Chair'),
        ('equipment', 'Equipment'),
        ('room', 'Room'),
        ('other', 'Other'),
    ]
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='chair')
    name = models.CharField(max_length=100)
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resources'
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Settings(models.Model):
    """
    Settings model - flexible key-value storage for organization/branch settings
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='settings',
        null=True,
        blank=True
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='settings',
        null=True,
        blank=True
    )
    key = models.CharField(max_length=100)
    value = models.JSONField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'settings'
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        unique_together = [['organization', 'branch', 'key']]
    
    def __str__(self):
        scope = self.branch.name if self.branch else self.organization.name if self.organization else 'Global'
        return f"{scope} - {self.key}"


class ClinicInfo(models.Model):
    """
    Clinic information model - реквизиты клиники
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='clinic_info'
    )
    
    # Реквизиты
    inn = models.CharField(max_length=20, blank=True, verbose_name='ИНН')
    kpp = models.CharField(max_length=20, blank=True, verbose_name='КПП')
    ogrn = models.CharField(max_length=20, blank=True, verbose_name='ОГРН')
    legal_name = models.CharField(max_length=500, blank=True, verbose_name='Юридическое название')
    legal_address = models.TextField(blank=True, verbose_name='Юридический адрес')
    
    # Контакты
    website = models.URLField(blank=True, verbose_name='Веб-сайт')
    support_email = models.EmailField(blank=True, verbose_name='Email поддержки')
    support_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон поддержки')
    
    # Лицензия
    license_number = models.CharField(max_length=100, blank=True, verbose_name='Номер лицензии')
    license_issued_date = models.DateField(null=True, blank=True, verbose_name='Дата выдачи лицензии')
    license_issued_by = models.CharField(max_length=500, blank=True, verbose_name='Кем выдана лицензия')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clinic_info'
        verbose_name = 'Clinic Info'
        verbose_name_plural = 'Clinic Info'
    
    def __str__(self):
        return f"Info for {self.organization.name}"

