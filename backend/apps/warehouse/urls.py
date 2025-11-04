from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, StockItemViewSet, StockBatchViewSet, StockMoveViewSet

router = DefaultRouter()
router.register('warehouses', WarehouseViewSet)
router.register('items', StockItemViewSet)
router.register('batches', StockBatchViewSet)
router.register('moves', StockMoveViewSet)

urlpatterns = [path('', include(router.urls))]
