from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsWarehouse
from django.db.models import Sum, Q
from .models import Warehouse, StockItem, StockBatch, StockMove
from .serializers import (
    WarehouseSerializer, StockItemSerializer, StockItemListSerializer,
    StockBatchSerializer, StockMoveSerializer
)


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only require warehouse permission for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsWarehouse()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by organization
        if user.is_superuser:
            qs = Warehouse.objects.all()
        elif user.organization:
            qs = Warehouse.objects.filter(branch__organization=user.organization)
        else:
            qs = Warehouse.objects.none()
        
        # Фильтры
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        
        branch_id = self.request.query_params.get('branch')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        
        return qs.select_related('branch').order_by('-created_at')
    
    def perform_create(self, serializer):
        # Автоматически устанавливаем организацию из branch
        serializer.save()


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only require warehouse permission for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsWarehouse()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by organization
        if user.is_superuser:
            qs = StockItem.objects.all()
        elif user.organization:
            qs = StockItem.objects.filter(organization=user.organization)
        else:
            qs = StockItem.objects.none()
        
        # Поиск
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(unit__icontains=search))
        
        # Фильтры
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        
        low_stock = self.request.query_params.get('low_stock')
        if low_stock and low_stock.lower() == 'true':
            # Фильтр по низкому остатку будет на фронтенде, т.к. это вычисляемое поле
            pass
        
        return qs.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=False, methods=['get'])
    def list_simple(self, request):
        """Простой список для селектов"""
        items = self.get_queryset().filter(is_active=True)
        serializer = StockItemListSerializer(items, many=True)
        return Response(serializer.data)


class StockBatchViewSet(viewsets.ModelViewSet):
    queryset = StockBatch.objects.all()
    serializer_class = StockBatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only require warehouse permission for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsWarehouse()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by organization
        if user.is_superuser:
            qs = StockBatch.objects.all()
        elif user.organization:
            qs = StockBatch.objects.filter(warehouse__branch__organization=user.organization)
        else:
            qs = StockBatch.objects.none()
        
        # Фильтры
        warehouse_id = self.request.query_params.get('warehouse')
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        
        stockitem_id = self.request.query_params.get('stockitem')
        if stockitem_id:
            qs = qs.filter(stockitem_id=stockitem_id)
        
        # Фильтр по просроченным
        expired = self.request.query_params.get('expired')
        if expired and expired.lower() == 'true':
            from django.utils import timezone
            qs = qs.filter(exp_date__lt=timezone.now().date())
        
        return qs.select_related('stockitem', 'warehouse').order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def inventory(self, request):
        """Сводка по остаткам на складах"""
        user = request.user
        
        # Filter by organization
        if user.is_superuser:
            queryset = StockBatch.objects.all()
        elif user.organization:
            queryset = StockBatch.objects.filter(
                warehouse__branch__organization=user.organization
            )
        else:
            queryset = StockBatch.objects.none()
        
        batches = queryset.values(
            'stockitem__id',
            'stockitem__name', 
            'stockitem__unit',
            'stockitem__min_quantity',
            'warehouse__id',
            'warehouse__name'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('stockitem__name', 'warehouse__name')
        
        return Response(batches)


class StockMoveViewSet(viewsets.ModelViewSet):
    queryset = StockMove.objects.all()
    serializer_class = StockMoveSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only require warehouse permission for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsWarehouse()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by organization
        if user.is_superuser:
            qs = StockMove.objects.all()
        elif user.organization:
            qs = StockMove.objects.filter(branch__organization=user.organization)
        else:
            qs = StockMove.objects.none()
        
        # Фильтры
        move_type = self.request.query_params.get('type')
        if move_type:
            qs = qs.filter(type=move_type)
        
        stockitem_id = self.request.query_params.get('stockitem')
        if stockitem_id:
            qs = qs.filter(stockitem_id=stockitem_id)
        
        return qs.select_related('stockitem', 'branch', 'batch').order_by('-created_at')
    
    def perform_create(self, serializer):
        # При создании движения обновляем остатки в партии
        move = serializer.save()
        
        if move.batch:
            if move.type == 'in':
                move.batch.quantity += move.qty
            elif move.type == 'out':
                move.batch.quantity -= move.qty
            move.batch.save()

