from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCategoryViewSet,
    ServiceViewSet,
    PriceListViewSet,
    PriceItemViewSet,
    ICDCodeViewSet
)

router = DefaultRouter()
router.register('categories', ServiceCategoryViewSet, basename='category')
router.register('services', ServiceViewSet, basename='service')
router.register('pricelists', PriceListViewSet, basename='pricelist')
router.register('priceitems', PriceItemViewSet, basename='priceitem')
router.register('icd', ICDCodeViewSet, basename='icd')

urlpatterns = [
    path('', include(router.urls)),
]
