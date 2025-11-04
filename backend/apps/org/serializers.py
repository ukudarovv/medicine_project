from rest_framework import serializers
from .models import Organization, Branch, Room, Resource, Settings, ClinicInfo


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Organization serializer
    """
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'sms_sender', 'logo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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

