from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeeBranchViewSet, EmployeeServiceViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register('employee-branches', EmployeeBranchViewSet, basename='employee-branch')
router.register('employee-services', EmployeeServiceViewSet, basename='employee-service')

urlpatterns = [
    path('', include(router.urls)),
]
