from django.contrib import admin
from .models import Warehouse, StockItem, StockBatch, StockMove


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'is_active']
    raw_id_fields = ['branch']


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'min_quantity', 'is_active']
    raw_id_fields = ['organization']


@admin.register(StockBatch)
class StockBatchAdmin(admin.ModelAdmin):
    list_display = ['stockitem', 'warehouse', 'lot', 'quantity', 'exp_date']
    raw_id_fields = ['stockitem', 'warehouse']


@admin.register(StockMove)
class StockMoveAdmin(admin.ModelAdmin):
    list_display = ['stockitem', 'branch', 'type', 'qty', 'created_at']
    list_filter = ['type', 'created_at']
    raw_id_fields = ['branch', 'stockitem', 'batch', 'ref_visit']

