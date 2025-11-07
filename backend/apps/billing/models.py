from django.db import models
from apps.org.models import Branch
from apps.visits.models import Visit


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('canceled', 'Отменён'),
    ]
    
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='invoices')
    number = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.number}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('kaspi', 'Kaspi'),
        ('kaspi_qr', 'Kaspi QR'),  # Sprint 4
        ('halyk_pay', 'Halyk Pay'),  # Sprint 4
        ('paybox', 'Paybox'),  # Sprint 4
        ('cloud', 'Cloud Payments'),
    ]
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('completed', 'Завершён'),
        ('failed', 'Ошибка'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=100, blank=True)
    ext_id = models.CharField(max_length=200, blank=True, help_text='External payment ID from provider')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Additional fields for KZ payment providers
    qr_code_url = models.URLField(blank=True, help_text='URL for QR code image (Kaspi QR)')
    redirect_url = models.URLField(blank=True, help_text='Redirect URL for payment page (Halyk Pay)')
    callback_data = models.JSONField(default=dict, blank=True, help_text='Callback data from provider')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']


class CashShift(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='cash_shifts')
    opened_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, related_name='opened_shifts')
    closed_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_shifts')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'cash_shifts'
        ordering = ['-opened_at']


# ==================== Sprint 4: KZ Payment Providers ====================


class PaymentProvider(models.Model):
    """
    Payment provider configuration (Kaspi, Halyk, etc.) - Sprint 4
    """
    PROVIDER_TYPES = [
        ('kaspi', 'Kaspi QR'),
        ('halyk', 'Halyk Pay'),
        ('paybox', 'Paybox'),
    ]
    
    organization = models.ForeignKey(
        'org.Organization',
        on_delete=models.CASCADE,
        related_name='payment_providers'
    )
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    merchant_id = models.CharField(max_length=200, help_text='Merchant ID')
    api_key = models.CharField(max_length=500, help_text='API key (encrypted)')
    api_secret = models.CharField(max_length=500, blank=True, help_text='API secret (encrypted)')
    webhook_url = models.URLField(blank=True, help_text='Webhook URL for payment notifications')
    is_active = models.BooleanField(default=True)
    
    # Test mode flag
    is_test_mode = models.BooleanField(default=True, help_text='Test/Sandbox mode')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_providers'
        verbose_name = 'Payment Provider'
        verbose_name_plural = 'Payment Providers'
        unique_together = ['organization', 'provider_type']
    
    def __str__(self):
        return f"{self.organization.name} - {self.get_provider_type_display()}"


class TaxDeductionCertificate(models.Model):
    """
    Tax deduction certificate (Kazakhstan) - Sprint 4
    Справка для налогового вычета
    """
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('issued', 'Выдана'),
        ('cancelled', 'Отменена'),
    ]
    
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='tax_certificates'
    )
    year = models.IntegerField(help_text='Налоговый год')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Общая сумма расходов')
    
    # Services list with amounts
    services_list = models.JSONField(
        default=list,
        help_text='Список услуг: [{"service": "...", "date": "...", "amount": 0}]'
    )
    
    # Certificate details
    certificate_number = models.CharField(max_length=50, unique=True, help_text='Номер справки')
    issued_date = models.DateField(help_text='Дата выдачи')
    issued_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_tax_certificates'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tax_deduction_certificates'
        verbose_name = 'Tax Deduction Certificate'
        verbose_name_plural = 'Tax Deduction Certificates'
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['patient', 'year']),
            models.Index(fields=['certificate_number']),
        ]
    
    def __str__(self):
        return f"Справка № {self.certificate_number} - {self.patient.full_name} ({self.year})"
    
    def generate_number(self):
        """Generate certificate number: СНВ-{year}-{org_id}-{seq}"""
        if not self.certificate_number:
            # Find max sequence for this year and organization
            org = self.patient.organization
            last_cert = TaxDeductionCertificate.objects.filter(
                patient__organizations=org,
                year=self.year
            ).exclude(id=self.id).order_by('-certificate_number').first()
            
            if last_cert and last_cert.certificate_number:
                # Extract sequence number
                try:
                    parts = last_cert.certificate_number.split('-')
                    seq = int(parts[-1]) + 1
                except:
                    seq = 1
            else:
                seq = 1
            
            self.certificate_number = f"СНВ-{self.year}-{org.id}-{seq:04d}"
        return self.certificate_number

