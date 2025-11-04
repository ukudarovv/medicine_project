from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet, PaymentViewSet, CashShiftViewSet,
    TaxDeductionCertificateViewSet, PaymentProviderViewSet
)

router = DefaultRouter()
router.register('invoices', InvoiceViewSet)
router.register('payments', PaymentViewSet)
router.register('cashshifts', CashShiftViewSet)
router.register('tax-certificates', TaxDeductionCertificateViewSet)
router.register('payment-providers', PaymentProviderViewSet)

urlpatterns = [path('', include(router.urls))]
