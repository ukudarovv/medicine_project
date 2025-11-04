from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailabilityViewSet, AppointmentViewSet, AppointmentResourceViewSet

router = DefaultRouter()
router.register('availability', AvailabilityViewSet, basename='availability')
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register('appointment-resources', AppointmentResourceViewSet, basename='appointment-resource')

urlpatterns = [
    path('', include(router.urls)),
]
