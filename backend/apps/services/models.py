from django.db import models
from apps.org.models import Organization, Branch


class ServiceCategory(models.Model):
    """
    Service category model - hierarchical tree structure
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='service_categories'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_categories'
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['order', 'name']
        unique_together = ['organization', 'code']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class Service(models.Model):
    """
    Service model - medical services/procedures
    """
    UNIT_CHOICES = [
        ('service', 'Услуга'),
        ('piece', 'Штука'),
        ('hour', 'Час'),
        ('visit', 'Визит'),
        ('tooth', 'Зуб'),
        ('unit', 'Единица'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='services'
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    
    # Basic info
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Pricing
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='service')
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Базовая цена'
    )
    price_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Минимальная цена (если диапазон)'
    )
    price_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Максимальная цена (если диапазон)'
    )
    
    # Tax
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Ставка НДС (%)'
    )
    
    # Duration and scheduling
    default_duration = models.IntegerField(
        default=30,
        help_text='Длительность в минутах'
    )
    
    # Visual
    color = models.CharField(
        max_length=7,
        default='#2196F3',
        help_text='Цвет в календаре (hex)'
    )
    image = models.ImageField(
        upload_to='services/',
        null=True,
        blank=True,
        help_text='Изображение для онлайн-записи'
    )
    
    # Flags
    is_expensive = models.BooleanField(
        default=False,
        help_text='Дорогая услуга (требует одобрения)'
    )
    is_active = models.BooleanField(default=True)
    show_in_online_booking = models.BooleanField(default=True)
    
    # Materials and resources
    requires_materials = models.BooleanField(default=False)
    requires_equipment = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']
        unique_together = ['organization', 'code']
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"[{self.code}] {self.name}"


class PriceList(models.Model):
    """
    Price list model - for managing prices over time
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='pricelists'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='pricelists',
        help_text='Прайс для конкретного филиала (если null - для всей организации)'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(help_text='Дата начала действия')
    end_date = models.DateField(null=True, blank=True, help_text='Дата окончания действия')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pricelists'
        verbose_name = 'Price List'
        verbose_name_plural = 'Price Lists'
        ordering = ['-start_date']
    
    def __str__(self):
        scope = self.branch.name if self.branch else self.organization.name
        return f"{self.name} ({scope}) - {self.start_date}"


class PriceItem(models.Model):
    """
    Price item - service price in a specific price list
    """
    pricelist = models.ForeignKey(
        PriceList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='price_items'
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Скидка на услугу в этом прайсе (%)'
    )
    
    class Meta:
        db_table = 'pricelist_items'
        verbose_name = 'Price Item'
        verbose_name_plural = 'Price Items'
        unique_together = ['pricelist', 'service']
    
    def __str__(self):
        return f"{self.service.name} - {self.price} ({self.pricelist.name})"
    
    @property
    def final_price(self):
        """Calculate final price after discount"""
        if self.discount_percent:
            return self.price * (1 - self.discount_percent / 100)
        return self.price


class ICDCode(models.Model):
    """
    ICD-10 codes (МКБ-10)
    """
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    name_ru = models.CharField(max_length=500, blank=True)
    parent_code = models.CharField(max_length=10, blank=True)
    level = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'icd_codes'
        verbose_name = 'ICD Code'
        verbose_name_plural = 'ICD Codes'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['parent_code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name_ru or self.name}"


class ServiceMaterial(models.Model):
    """
    Materials required for a service
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='required_materials'
    )
    material = models.ForeignKey(
        'warehouse.StockItem',
        on_delete=models.CASCADE,
        related_name='service_usages'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text='Количество материала на 1 единицу услуги'
    )
    is_optional = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'service_materials'
        verbose_name = 'Service Material'
        verbose_name_plural = 'Service Materials'
        unique_together = ['service', 'material']
    
    def __str__(self):
        return f"{self.service.name} - {self.material.name} (x{self.quantity})"

