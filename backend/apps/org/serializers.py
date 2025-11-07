from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.core.models import User
from .models import Organization, Branch, Room, Resource, Settings, ClinicInfo


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Organization serializer
    """
    branches_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'sms_sender', 'logo', 'created_at', 'updated_at', 'branches_count', 'users_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_branches_count(self, obj):
        return obj.branches.count()
    
    def get_users_count(self, obj):
        return obj.users.count()


class OrganizationUserSerializer(serializers.ModelSerializer):
    """
    Serializer for users in an organization
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class OrganizationUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users in an organization
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RoomSerializer(serializers.ModelSerializer):
    """
    Room serializer
    """
    
    class Meta:
        model = Room
        fields = ['id', 'branch', 'name', 'color', 'is_active', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ResourceSerializer(serializers.ModelSerializer):
    """
    Resource serializer
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Resource
        fields = [
            'id', 'branch', 'type', 'type_display', 'name',
            'room', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BranchSerializer(serializers.ModelSerializer):
    """
    Branch serializer
    """
    rooms = RoomSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id', 'organization', 'name', 'address', 'phone', 'email',
            'timezone', 'work_hours_from', 'work_hours_to', 'is_active',
            'rooms', 'resources', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchListSerializer(serializers.ModelSerializer):
    """
    Simplified branch serializer for lists
    """
    
    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'address', 'phone', 'email',
            'timezone', 'is_active'
        ]


class SettingsSerializer(serializers.ModelSerializer):
    """
    Settings serializer
    """
    
    class Meta:
        model = Settings
        fields = ['id', 'organization', 'branch', 'key', 'value', 'description', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class ClinicInfoSerializer(serializers.ModelSerializer):
    """
    Clinic information serializer
    """
    
    class Meta:
        model = ClinicInfo
        fields = [
            'id', 'organization', 'inn', 'kpp', 'ogrn',
            'legal_name', 'legal_address', 'website',
            'support_email', 'support_phone',
            'license_number', 'license_issued_date', 'license_issued_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

