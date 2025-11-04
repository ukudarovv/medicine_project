from rest_framework import serializers
from .models import Employee, EmployeeBranch, EmployeeService
from apps.core.serializers import UserSerializer
from apps.core.models import User


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
    Employee serializer
    """
    full_name = serializers.CharField(read_only=True)
    user_info = UserSerializer(source='user', read_only=True)
    branches = EmployeeBranchSerializer(source='branch_assignments', many=True, read_only=True)
    services = EmployeeServiceSerializer(source='service_assignments', many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'organization', 'user', 'user_info',
            'first_name', 'last_name', 'middle_name', 'full_name',
            'phone', 'email', 'position', 'specialization',
            'hire_date', 'fire_date', 'iin',
            'passport_series', 'passport_number', 'passport_issued_by', 'passport_issued_date',
            'commission_percent', 'salary', 'color',
            'is_active', 'branches', 'services',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Simplified employee serializer for lists
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'position', 'specialization', 'phone', 'color', 'is_active'
        ]


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
        employee.save(update_fields=['user'])
        
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

