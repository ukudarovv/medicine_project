from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisitViewSet, VisitServiceViewSet, VisitPrescriptionViewSet, VisitResourceViewSet

router = DefaultRouter()
router.register('visits', VisitViewSet, basename='visit')
router.register('visit-services', VisitServiceViewSet, basename='visit-service')
router.register('visit-prescriptions', VisitPrescriptionViewSet, basename='visit-prescription')
router.register('visit-resources', VisitResourceViewSet, basename='visit-resource')

urlpatterns = [
    path('', include(router.urls)),
]
