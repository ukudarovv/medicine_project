from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, EmployeeBranchViewSet, EmployeeServiceViewSet,
    PositionViewSet, SalarySchemaTemplateViewSet, EmployeeSalarySchemaViewSet,
    EmployeeTaskViewSet, EmployeeResultViewSet
)

router = DefaultRouter()

# Employee endpoints
router.register('employees', EmployeeViewSet, basename='employee')
router.register('employee-branches', EmployeeBranchViewSet, basename='employee-branch')
router.register('employee-services', EmployeeServiceViewSet, basename='employee-service')

# Position endpoints
router.register('positions', PositionViewSet, basename='position')

# Salary schema endpoints
router.register('salary-templates', SalarySchemaTemplateViewSet, basename='salary-template')
router.register('salary-schemas', EmployeeSalarySchemaViewSet, basename='salary-schema')

# Task and result endpoints
router.register('tasks', EmployeeTaskViewSet, basename='task')
router.register('results', EmployeeResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls)),
]
