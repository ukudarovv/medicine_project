from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsWarehouse
from .models import Warehouse, StockItem, StockBatch, StockMove
from .serializers import WarehouseSerializer, StockItemSerializer, StockBatchSerializer, StockMoveSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        return Warehouse.objects.filter(branch__organization=user.organization)


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        return StockItem.objects.filter(organization=user.organization)


class StockBatchViewSet(viewsets.ModelViewSet):
    queryset = StockBatch.objects.all()
    serializer_class = StockBatchSerializer
    permission_classes = [IsAuthenticated, IsWarehouse]
    
    def get_queryset(self):
        user = self.request.user
        return StockBatch.objects.filter(warehouse__branch__organization=user.organization)


class StockMoveViewSet(viewsets.ModelViewSet):
    queryset = StockMove.objects.all()
    serializer_class = StockMoveSerializer
    permission_classes = [IsAuthenticated, IsWarehouse]
    
    def get_queryset(self):
        user = self.request.user
        return StockMove.objects.filter(branch__organization=user.organization)

