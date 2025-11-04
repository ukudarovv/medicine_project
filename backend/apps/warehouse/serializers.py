from rest_framework import serializers
from .models import Warehouse, StockItem, StockBatch, StockMove


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'branch', 'name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = ['id', 'organization', 'name', 'unit', 'min_quantity', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockBatch
        fields = ['id', 'stockitem', 'warehouse', 'lot', 'exp_date', 'quantity', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMove
        fields = ['id', 'branch', 'stockitem', 'batch', 'qty', 'type', 'ref_visit', 'created_at']
        read_only_fields = ['id', 'created_at']

