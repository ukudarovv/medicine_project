from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.utils import timezone

from apps.core.permissions import IsBranchMember, IsBranchAdmin
from .models import (
    Employee, EmployeeBranch, EmployeeService, Position,
    SalarySchemaTemplate, EmployeeSalarySchema,
    EmployeeTask, EmployeeTaskComment, EmployeeTaskAttachment,
    EmployeeResult
)
from .serializers import (
    EmployeeSerializer, EmployeeListSerializer, EmployeeBranchSerializer,
    EmployeeServiceSerializer, GrantAccessSerializer,
    PositionSerializer, PositionListSerializer,
    SalarySchemaTemplateSerializer, SalarySchemaTemplateListSerializer,
    EmployeeSalarySchemaSerializer, ApplySalaryTemplateSerializer,
    EmployeeTaskSerializer, EmployeeTaskListSerializer, EmployeeTaskDetailSerializer,
    EmployeeTaskCommentSerializer, EmployeeTaskAttachmentSerializer,
    EmployeeResultSerializer, EmployeeResultListSerializer
)


class PositionViewSet(viewsets.ModelViewSet):
    """
    Position CRUD
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hidden_in_schedule_filter']
    search_fields = ['name', 'comment']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        return Position.objects.filter(organization=user.organization)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PositionListSerializer
        return PositionSerializer
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class SalarySchemaTemplateViewSet(viewsets.ModelViewSet):
    """
    Salary schema template CRUD
    """
    queryset = SalarySchemaTemplate.objects.all()
    serializer_class = SalarySchemaTemplateSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        return SalarySchemaTemplate.objects.filter(organization=user.organization)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalarySchemaTemplateListSerializer
        return SalarySchemaTemplateSerializer
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBranchAdmin])
    def apply_to_employees(self, request, pk=None):
        """
        Apply salary template to multiple employees
        """
        template = self.get_object()
        serializer = ApplySalaryTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee_ids = serializer.validated_data['employee_ids']
        starts_at = serializer.validated_data['starts_at']
        ends_at = serializer.validated_data.get('ends_at')
        
        # Verify employees belong to same organization
        employees = Employee.objects.filter(
            id__in=employee_ids,
            organization=request.user.organization
        )
        
        if employees.count() != len(employee_ids):
            return Response(
                {'error': 'Some employees not found or not in your organization'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create salary schema assignments
        created = []
        for employee in employees:
            schema = EmployeeSalarySchema.objects.create(
                employee=employee,
                salary_template=template,
                starts_at=starts_at,
                ends_at=ends_at,
                is_active=True,
                created_by=request.user
            )
            created.append(EmployeeSalarySchemaSerializer(schema).data)
        
        return Response(
            {'created': created, 'count': len(created)},
            status=status.HTTP_201_CREATED
        )


class EmployeeSalarySchemaViewSet(viewsets.ModelViewSet):
    """
    Employee salary schema assignment CRUD
    """
    queryset = EmployeeSalarySchema.objects.all()
    serializer_class = EmployeeSalarySchemaSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['employee', 'salary_template', 'is_active']
    ordering_fields = ['starts_at', 'created_at']
    ordering = ['-starts_at']
    
    def get_queryset(self):
        user = self.request.user
        return EmployeeSalarySchema.objects.filter(
            employee__organization=user.organization
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmployeeResultViewSet(viewsets.ModelViewSet):
    """
    Employee result (task result reference) CRUD
    """
    queryset = EmployeeResult.objects.all()
    serializer_class = EmployeeResultSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'comment']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        queryset = EmployeeResult.objects.filter(organization=user.organization)
        
        # Filter by position if provided
        position_id = self.request.query_params.get('position')
        if position_id:
            queryset = queryset.filter(positions__id=position_id).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeResultListSerializer
        return EmployeeResultSerializer
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class EmployeeTaskViewSet(viewsets.ModelViewSet):
    """
    Employee task CRUD
    """
    queryset = EmployeeTask.objects.all()
    serializer_class = EmployeeTaskSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['assignee', 'author', 'status', 'result']
    search_fields = ['title', 'description']
    ordering_fields = ['deadline_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = EmployeeTask.objects.filter(organization=user.organization)
        
        # Date range filters
        deadline_from = self.request.query_params.get('deadline_from')
        deadline_to = self.request.query_params.get('deadline_to')
        
        if deadline_from:
            queryset = queryset.filter(deadline_at__gte=deadline_from)
        if deadline_to:
            queryset = queryset.filter(deadline_at__lte=deadline_to)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeTaskListSerializer
        elif self.action == 'retrieve':
            return EmployeeTaskDetailSerializer
        return EmployeeTaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            author=self.request.user
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        """
        Add comment to task
        """
        task = self.get_object()
        serializer = EmployeeTaskCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_attachment(self, request, pk=None):
        """
        Upload file attachment to task
        """
        task = self.get_object()
        serializer = EmployeeTaskAttachmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, uploaded_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_status(self, request, pk=None):
        """
        Change task status
        """
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(EmployeeTask.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = new_status
        
        # Set completed_at if status is done
        if new_status == 'done' and not task.completed_at:
            task.completed_at = timezone.now()
        
        task.save()
        
        return Response(EmployeeTaskDetailSerializer(task).data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee CRUD with extended HR functionality
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['position', 'employment_status', 'is_active', 'show_in_schedule']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'iin']
    ordering_fields = ['last_name', 'hired_at', 'created_at']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.query_params.get('branch')
        
        # Filter by organization
        if user.is_superuser:
            queryset = Employee.objects.all()
        elif user.organization:
            queryset = Employee.objects.filter(organization=user.organization)
        else:
            queryset = Employee.objects.none()
        
        # Filter by branch if provided
        if branch_id:
            queryset = queryset.filter(
                branch_assignments__branch_id=branch_id
            ).distinct()
        
        # Date range filters for hiring
        hired_from = self.request.query_params.get('hired_from')
        hired_to = self.request.query_params.get('hired_to')
        
        if hired_from:
            queryset = queryset.filter(hired_at__gte=hired_from)
        if hired_to:
            queryset = queryset.filter(hired_at__lte=hired_to)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBranchAdmin])
    def toggle_user_access(self, request, pk=None):
        """
        Enable/disable user access for employee
        """
        employee = self.get_object()
        
        if not employee.user:
            return Response(
                {'error': 'Employee has no user account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee.is_user_enabled = not employee.is_user_enabled
        employee.save(update_fields=['is_user_enabled'])
        
        # Also update User.is_active
        employee.user.is_active = employee.is_user_enabled
        employee.user.save(update_fields=['is_active'])
        
        return Response({
            'is_user_enabled': employee.is_user_enabled
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsBranchAdmin])
    def assign_salary_schema(self, request, pk=None):
        """
        Assign salary schema to employee
        """
        employee = self.get_object()
        serializer = EmployeeSalarySchemaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee, created_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsBranchAdmin])
    def remove_salary_schema(self, request, pk=None):
        """
        Remove (deactivate) salary schema from employee
        """
        employee = self.get_object()
        schema_id = request.query_params.get('schema_id')
        
        if not schema_id:
            return Response(
                {'error': 'schema_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            schema = EmployeeSalarySchema.objects.get(
                id=schema_id,
                employee=employee
            )
            schema.is_active = False
            schema.ends_at = timezone.now().date()
            schema.save()
            
            return Response({'status': 'deactivated'})
        except EmployeeSalarySchema.DoesNotExist:
            return Response(
                {'error': 'Salary schema not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def doctors(self, request):
        """
        Get list of doctors only
        """
        queryset = self.get_queryset().filter(
            models.Q(position__name__icontains='врач') |
            models.Q(position__name__icontains='doctor') |
            models.Q(position_legacy__icontains='врач') |
            models.Q(position_legacy__icontains='doctor')
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'branch', 'is_default']
    
    def get_queryset(self):
        user = self.request.user
        return EmployeeBranch.objects.filter(
            employee__organization=user.organization
        )


class EmployeeServiceViewSet(viewsets.ModelViewSet):
    """
    Employee-Service assignment CRUD
    """
    queryset = EmployeeService.objects.all()
    serializer_class = EmployeeServiceSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'service']
    
    def get_queryset(self):
        user = self.request.user
        return EmployeeService.objects.filter(
            employee__organization=user.organization
        )
