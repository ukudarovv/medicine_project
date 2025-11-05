from rest_framework import serializers
from .models import Warehouse, StockItem, StockBatch, StockMove
from apps.org.models import Branch
from django.db.models import Sum, F


class BranchSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']


class WarehouseSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    batches_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = ['id', 'branch', 'branch_name', 'name', 'is_active', 'batches_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'branch_name', 'batches_count']
    
    def get_batches_count(self, obj):
        return obj.batches.count()


class StockItemSerializer(serializers.ModelSerializer):
    current_quantity = serializers.SerializerMethodField()
    low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = StockItem
        fields = ['id', 'organization', 'name', 'unit', 'min_quantity', 'is_active', 
                  'current_quantity', 'low_stock', 'created_at']
        read_only_fields = ['id', 'organization', 'created_at', 'current_quantity', 'low_stock']
    
    def get_current_quantity(self, obj):
        total = obj.batches.aggregate(total=Sum('quantity'))['total']
        return float(total) if total else 0.0
    
    def get_low_stock(self, obj):
        current = self.get_current_quantity(obj)
        return current < float(obj.min_quantity)


class StockItemListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = StockItem
        fields = ['id', 'name', 'unit']


class StockBatchSerializer(serializers.ModelSerializer):
    stockitem_name = serializers.CharField(source='stockitem.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    stockitem_unit = serializers.CharField(source='stockitem.unit', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = StockBatch
        fields = ['id', 'stockitem', 'stockitem_name', 'stockitem_unit', 'warehouse', 
                  'warehouse_name', 'lot', 'exp_date', 'quantity', 'is_expired', 'created_at']
        read_only_fields = ['id', 'created_at', 'stockitem_name', 'warehouse_name', 
                            'stockitem_unit', 'is_expired']
    
    def get_is_expired(self, obj):
        if obj.exp_date:
            from django.utils import timezone
            return obj.exp_date < timezone.now().date()
        return False


class StockMoveSerializer(serializers.ModelSerializer):
    stockitem_name = serializers.CharField(source='stockitem.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = StockMove
        fields = ['id', 'branch', 'branch_name', 'stockitem', 'stockitem_name', 
                  'batch', 'qty', 'type', 'type_display', 'ref_visit', 'created_at']
        read_only_fields = ['id', 'created_at', 'stockitem_name', 'branch_name', 'type_display']

