from django.db import models
from apps.org.models import Organization, Branch


class Warehouse(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='warehouses')
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warehouses'
    
    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class StockItem(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='stock_items')
    name = models.CharField(max_length=500)
    unit = models.CharField(max_length=50)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_items'
    
    def __str__(self):
        return self.name


class StockBatch(models.Model):
    stockitem = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='batches')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='batches')
    lot = models.CharField(max_length=100, blank=True)
    exp_date = models.DateField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_batches'


class StockMove(models.Model):
    MOVE_TYPES = [
        ('in', 'Приход'),
        ('out', 'Расход'),
        ('transfer', 'Перемещение'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stock_moves')
    stockitem = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='moves')
    batch = models.ForeignKey(StockBatch, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=MOVE_TYPES)
    ref_visit = models.ForeignKey('visits.Visit', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_moves'
        ordering = ['-created_at']

