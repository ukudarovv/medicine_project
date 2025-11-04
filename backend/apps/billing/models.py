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
    ext_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
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

