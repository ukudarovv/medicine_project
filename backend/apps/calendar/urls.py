from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvailabilityViewSet, 
    AppointmentViewSet, 
    AppointmentResourceViewSet,
    WaitlistViewSet,
    BreakViewSet
)

router = DefaultRouter()
router.register('availability', AvailabilityViewSet, basename='availability')
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register('appointment-resources', AppointmentResourceViewSet, basename='appointment-resource')
router.register('waitlist', WaitlistViewSet, basename='waitlist')
router.register('breaks', BreakViewSet, basename='break')

urlpatterns = [
    path('', include(router.urls)),
]
