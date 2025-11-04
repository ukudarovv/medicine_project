from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsBranchAdmin
from .models import Employee, EmployeeBranch, EmployeeService
from .serializers import (
    EmployeeSerializer,
    EmployeeListSerializer,
    EmployeeBranchSerializer,
    EmployeeServiceSerializer,
    GrantAccessSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee CRUD
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.query_params.get('branch')
        
        queryset = Employee.objects.filter(organization=user.organization)
        
        # Filter by branch if provided
        if branch_id:
            queryset = queryset.filter(
                branch_assignments__branch_id=branch_id
            ).distinct()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBranchAdmin])
    def grant_access(self, request, pk=None):
        """
        Grant system access to employee by creating a User account
        """
        employee = self.get_object()
        
        if employee.user:
            return Response(
                {'error': 'Employee already has system access'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = GrantAccessSerializer(
            data=request.data,
            context={'employee': employee}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def doctors(self, request):
        """
        Get list of doctors only
        """
        queryset = self.get_queryset().filter(
            position__icontains='врач'
        ) | self.get_queryset().filter(
            position__icontains='doctor'
        )
        
        serializer = EmployeeListSerializer(queryset, many=True)
        return Response(serializer.data)


class EmployeeBranchViewSet(viewsets.ModelViewSet):
    """
    Employee-Branch assignment CRUD
    """
    queryset = EmployeeBranch.objects.all()
    serializer_class = EmployeeBranchSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_queryset(self):
        user = self.request.user
        employee_id = self.request.query_params.get('employee')
        
        queryset = EmployeeBranch.objects.filter(
            employee__organization=user.organization
        )
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset


class EmployeeServiceViewSet(viewsets.ModelViewSet):
    """
    Employee-Service assignment CRUD
    """
    queryset = EmployeeService.objects.all()
    serializer_class = EmployeeServiceSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_queryset(self):
        user = self.request.user
        employee_id = self.request.query_params.get('employee')
        
        queryset = EmployeeService.objects.filter(
            employee__organization=user.organization
        )
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset

