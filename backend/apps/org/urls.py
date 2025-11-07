from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet,
    BranchViewSet,
    RoomViewSet,
    ResourceViewSet,
    SettingsViewSet,
    ClinicInfoView,
    OrganizationUserViewSet
)

router = DefaultRouter()
router.register('organizations', OrganizationViewSet, basename='organization')
router.register('organization-users', OrganizationUserViewSet, basename='organization-user')
router.register('branches', BranchViewSet, basename='branch')
router.register('rooms', RoomViewSet, basename='room')
router.register('resources', ResourceViewSet, basename='resource')
router.register('settings', SettingsViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
    path('clinic-info/', ClinicInfoView.as_view(), name='clinic_info'),
]
