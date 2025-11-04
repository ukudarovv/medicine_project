from rest_framework import serializers
from .models import (
    Employee, EmployeeBranch, EmployeeService, Position,
    SalarySchemaTemplate, EmployeeSalarySchema,
    EmployeeTask, EmployeeTaskComment, EmployeeTaskAttachment,
    EmployeeResult, EmployeeResultPosition
)
from apps.core.serializers import UserSerializer
from apps.core.models import User


# ====================
# Position Serializers
# ====================

class PositionSerializer(serializers.ModelSerializer):
    """
    Position serializer
    """
    class Meta:
        model = Position
        fields = [
            'id', 'organization', 'name', 'comment',
            'hidden_in_schedule_filter', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionListSerializer(serializers.ModelSerializer):
    """
    Simplified position serializer for lists
    """
    class Meta:
        model = Position
        fields = ['id', 'name', 'hidden_in_schedule_filter']


# =================================
# Salary Schema Template Serializers
# =================================

class SalarySchemaTemplateSerializer(serializers.ModelSerializer):
    """
    Salary schema template serializer
    """
    class Meta:
        model = SalarySchemaTemplate
        fields = [
            'id', 'organization', 'name',
            # Commission settings
            'pct_of_own_sales', 'pct_value',
            'direction_bonus_enabled', 'direction_bonus_pct',
            'pct_per_created_visits_enabled', 'pct_per_visit',
            # Fixed salary and minimum
            'fixed_salary_enabled', 'fixed_amount', 'currency',
            'min_rate_enabled', 'min_rate_amount',
            # Additional settings
            'honor_patient_discount_enabled',
            'subscription_services_pct_enabled', 'subscription_pct',
            'calc_from_profit_instead_of_revenue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalarySchemaTemplateListSerializer(serializers.ModelSerializer):
    """
    Simplified salary template serializer for lists
    """
    class Meta:
        model = SalarySchemaTemplate
        fields = ['id', 'name', 'pct_of_own_sales', 'fixed_salary_enabled']


# =================================
# Employee Salary Schema Serializers
# =================================

class EmployeeSalarySchemaSerializer(serializers.ModelSerializer):
    """
    Employee salary schema assignment serializer
    """
    salary_template_name = serializers.CharField(source='salary_template.name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    salary_template_details = SalarySchemaTemplateSerializer(source='salary_template', read_only=True)
    
    class Meta:
        model = EmployeeSalarySchema
        fields = [
            'id', 'employee', 'employee_name', 'salary_template',
            'salary_template_name', 'salary_template_details',
            'starts_at', 'ends_at', 'is_active',
            'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at']


# =================================
# Employee Result Serializers
# =================================

class EmployeeResultSerializer(serializers.ModelSerializer):
    """
    Employee result serializer
    """
    positions = PositionListSerializer(many=True, read_only=True)
    position_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Position.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = EmployeeResult
        fields = [
            'id', 'organization', 'name', 'comment',
            'positions', 'position_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        position_ids = validated_data.pop('position_ids', [])
        result = EmployeeResult.objects.create(**validated_data)
        
        # Create EmployeeResultPosition records
        for position in position_ids:
            EmployeeResultPosition.objects.create(result=result, position=position)
        
        return result
    
    def update(self, instance, validated_data):
        position_ids = validated_data.pop('position_ids', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update positions if provided
        if position_ids is not None:
            # Remove old assignments
            EmployeeResultPosition.objects.filter(result=instance).delete()
            # Create new assignments
            for position in position_ids:
                EmployeeResultPosition.objects.create(result=instance, position=position)
        
        return instance


class EmployeeResultListSerializer(serializers.ModelSerializer):
    """
    Simplified result serializer for lists
    """
    class Meta:
        model = EmployeeResult
        fields = ['id', 'name']


# =================================
# Employee Task Serializers
# =================================

class EmployeeTaskCommentSerializer(serializers.ModelSerializer):
    """
    Task comment serializer
    """
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeTaskComment
        fields = ['id', 'task', 'author', 'author_name', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmployeeTaskAttachmentSerializer(serializers.ModelSerializer):
    """
    Task attachment serializer
    """
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeTaskAttachment
        fields = [
            'id', 'task', 'file', 'file_url', 'filename',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class EmployeeTaskSerializer(serializers.ModelSerializer):
    """
    Employee task serializer
    """
    assignee_name = serializers.CharField(source='assignee.full_name', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    result_name = serializers.CharField(source='result.name', read_only=True)
    comments = EmployeeTaskCommentSerializer(many=True, read_only=True)
    attachments = EmployeeTaskAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmployeeTask
        fields = [
            'id', 'organization', 'title', 'description',
            'assignee', 'assignee_name', 'author', 'author_name',
            'status', 'result', 'result_name',
            'deadline_at', 'completed_at',
            'comments', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeTaskListSerializer(serializers.ModelSerializer):
    """
    Simplified task serializer for lists
    """
    assignee_name = serializers.CharField(source='assignee.full_name', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    result_name = serializers.CharField(source='result.name', read_only=True)
    
    class Meta:
        model = EmployeeTask
        fields = [
            'id', 'title', 'assignee', 'assignee_name',
            'author_name', 'status', 'result_name',
            'deadline_at', 'created_at'
        ]


class EmployeeTaskDetailSerializer(EmployeeTaskSerializer):
    """
    Detailed task serializer with all relations
    """
    pass


# =================================
# Employee Serializers
# =================================

class EmployeeBranchSerializer(serializers.ModelSerializer):
    """
    Employee branch assignment serializer
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = EmployeeBranch
        fields = ['id', 'employee', 'branch', 'branch_name', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmployeeServiceSerializer(serializers.ModelSerializer):
    """
    Employee service assignment serializer
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_code = serializers.CharField(source='service.code', read_only=True)
    
    class Meta:
        model = EmployeeService
        fields = [
            'id', 'employee', 'service', 'service_name', 'service_code',
            'price_override', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Full employee serializer with all fields
    """
    full_name = serializers.CharField(read_only=True)
    user_info = UserSerializer(source='user', read_only=True)
    position_details = PositionSerializer(source='position', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    branches = EmployeeBranchSerializer(source='branch_assignments', many=True, read_only=True)
    services = EmployeeServiceSerializer(source='service_assignments', many=True, read_only=True)
    salary_schemas = EmployeeSalarySchemaSerializer(many=True, read_only=True)
    
    # Current active salary schema
    current_salary_schema = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'organization', 'user', 'user_info',
            # Personal info
            'first_name', 'last_name', 'middle_name', 'full_name',
            'phone', 'email',
            # Employment
            'position', 'position_details', 'position_legacy',
            'specialization', 'hired_at', 'fired_at', 'employment_status',
            # Legacy dates (for compatibility)
            'hire_date', 'fire_date',
            # Documents
            'iin', 'snils', 'inn',
            'passport_series', 'passport_number', 'passport_issued_by',
            'passport_issued_date', 'power_of_attorney_number',
            'power_of_attorney_date',
            # Flags
            'show_in_schedule', 'can_accept_payments', 'can_be_assistant',
            'limit_goods_sales_today_only',
            # Online booking
            'online_slot_step_minutes', 'min_gap_between_visits_minutes',
            'min_gap_between_days_hours',
            # Financial
            'markup_percent', 'commission_percent', 'salary',
            # Warehouse
            'warehouse', 'warehouse_name', 'warehouse_lock',
            # Printing flags
            'is_chief_accountant', 'is_cashier', 'is_org_head',
            # Calendar and access
            'calendar_color', 'color', 'access_template_id', 'is_user_enabled',
            # Additional
            'description', 'is_active',
            # Relations
            'branches', 'services', 'salary_schemas', 'current_salary_schema',
            # Meta
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']
    
    def get_current_salary_schema(self, obj):
        """Get currently active salary schema"""
        from django.utils import timezone
        today = timezone.now().date()
        
        active_schema = obj.salary_schemas.filter(
            is_active=True,
            starts_at__lte=today
        ).filter(
            models.Q(ends_at__gte=today) | models.Q(ends_at__isnull=True)
        ).first()
        
        if active_schema:
            return EmployeeSalarySchemaSerializer(active_schema).data
        return None


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Simplified employee serializer for lists
    """
    full_name = serializers.CharField(read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    current_salary_schema = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'position', 'position_name', 'specialization', 'phone',
            'calendar_color', 'is_active', 'employment_status',
            'hired_at', 'current_salary_schema'
        ]
    
    def get_current_salary_schema(self, obj):
        """Get currently active salary schema name"""
        from django.utils import timezone
        from django.db import models
        
        today = timezone.now().date()
        
        active_schema = obj.salary_schemas.filter(
            is_active=True,
            starts_at__lte=today
        ).filter(
            models.Q(ends_at__gte=today) | models.Q(ends_at__isnull=True)
        ).first()
        
        if active_schema:
            return {
                'id': active_schema.id,
                'name': active_schema.salary_template.name
            }
        return None


class GrantAccessSerializer(serializers.Serializer):
    """
    Serializer for granting system access to employee
    """
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    def validate(self, attrs):
        employee = self.context['employee']
        
        # Generate username if not provided
        if not attrs.get('username'):
            # Generate username from full name
            base_username = f"{employee.last_name.lower()}.{employee.first_name[0].lower()}"
            username = base_username
            
            # Check if username exists, add number if needed
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            attrs['username'] = username
        
        return attrs
    
    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        
        employee = self.context['employee']
        
        # Create user
        user = User.objects.create(
            username=validated_data['username'],
            password=make_password(validated_data['password']),
            email=employee.email,
            first_name=employee.first_name,
            last_name=employee.last_name,
            role=validated_data['role'],
            phone=employee.phone,
            organization=employee.organization
        )
        
        # Link user to employee
        employee.user = user
        employee.is_user_enabled = True
        employee.save(update_fields=['user', 'is_user_enabled'])
        
        # Create branch access based on employee's branches
        from apps.core.models import UserBranchAccess
        for branch_assignment in employee.branch_assignments.all():
            UserBranchAccess.objects.create(
                user=user,
                branch=branch_assignment.branch,
                is_default=branch_assignment.is_default
            )
        
        return {
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }


class ApplySalaryTemplateSerializer(serializers.Serializer):
    """
    Serializer for applying salary template to multiple employees
    """
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    starts_at = serializers.DateField()
    ends_at = serializers.DateField(required=False, allow_null=True)
    
    def validate(self, attrs):
        if attrs.get('ends_at') and attrs['starts_at'] >= attrs['ends_at']:
            raise serializers.ValidationError('ends_at must be after starts_at')
        return attrs
