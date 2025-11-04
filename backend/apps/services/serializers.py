from rest_framework import serializers
from .models import (
    ServiceCategory,
    Service,
    PriceList,
    PriceItem,
    ICDCode,
    ServiceMaterial
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    """
    Service category serializer with children
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'organization', 'parent', 'name', 'code',
            'description', 'order', 'is_active', 'children', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_children(self, obj):
        if hasattr(obj, 'prefetched_children'):
            children = obj.prefetched_children
        else:
            children = obj.children.filter(is_active=True)
        
        return ServiceCategorySerializer(children, many=True).data


class ServiceCategoryListSerializer(serializers.ModelSerializer):
    """
    Simplified category serializer for lists
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = ServiceCategory
        fields = ['id', 'parent', 'parent_name', 'name', 'code', 'order', 'is_active']


class ServiceMaterialSerializer(serializers.ModelSerializer):
    """
    Service material serializer
    """
    material_name = serializers.CharField(source='material.name', read_only=True)
    
    class Meta:
        model = ServiceMaterial
        fields = ['id', 'service', 'material', 'material_name', 'quantity', 'is_optional']
        read_only_fields = ['id']


class ServiceSerializer(serializers.ModelSerializer):
    """
    Service serializer
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    required_materials = ServiceMaterialSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'organization', 'category', 'category_name',
            'code', 'name', 'description',
            'unit', 'unit_display', 'base_price', 'price_min', 'price_max',
            'vat_rate', 'default_duration', 'color', 'image',
            'is_expensive', 'is_active', 'show_in_online_booking',
            'requires_materials', 'requires_equipment',
            'required_materials',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceListSerializer(serializers.ModelSerializer):
    """
    Simplified service serializer for lists
    """
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'category', 'code', 'name', 'category_name',
            'base_price', 'unit', 'default_duration', 'color', 'is_active'
        ]


class PriceItemSerializer(serializers.ModelSerializer):
    """
    Price item serializer
    """
    service_code = serializers.CharField(source='service.code', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    final_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = PriceItem
        fields = [
            'id', 'pricelist', 'service', 'service_code', 'service_name',
            'price', 'discount_percent', 'final_price'
        ]
        read_only_fields = ['id']


class PriceListSerializer(serializers.ModelSerializer):
    """
    Price list serializer
    """
    items = PriceItemSerializer(many=True, read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = PriceList
        fields = [
            'id', 'organization', 'branch', 'branch_name',
            'name', 'description', 'start_date', 'end_date',
            'is_active', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PriceListListSerializer(serializers.ModelSerializer):
    """
    Simplified price list serializer for lists
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PriceList
        fields = [
            'id', 'name', 'branch_name', 'start_date', 'end_date',
            'is_active', 'items_count'
        ]


class ICDCodeSerializer(serializers.ModelSerializer):
    """
    ICD code serializer
    """
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ICDCode
        fields = [
            'id', 'code', 'name', 'name_ru', 'display_name',
            'parent_code', 'level', 'is_active'
        ]
        read_only_fields = ['id']
    
    def get_display_name(self, obj):
        return obj.name_ru or obj.name

