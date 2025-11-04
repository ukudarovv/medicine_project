from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsBranchMember, IsBranchAdmin
from .models import (
    ServiceCategory,
    Service,
    PriceList,
    PriceItem,
    ICDCode,
    ServiceMaterial
)
from .serializers import (
    ServiceCategorySerializer,
    ServiceCategoryListSerializer,
    ServiceSerializer,
    ServiceListSerializer,
    PriceListSerializer,
    PriceListListSerializer,
    PriceItemSerializer,
    ICDCodeSerializer,
    ServiceMaterialSerializer
)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    Service category CRUD with tree structure
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    
    def get_queryset(self):
        user = self.request.user
        queryset = ServiceCategory.objects.filter(organization=user.organization)
        
        # Only root categories for tree view
        if self.request.query_params.get('root_only'):
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset.prefetch_related('children')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceCategoryListSerializer
        return ServiceCategorySerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get category tree structure
        """
        categories = self.get_queryset().filter(parent__isnull=True)
        serializer = ServiceCategorySerializer(categories, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    Service CRUD
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_expensive']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'base_price']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Service.objects.filter(organization=user.organization)
        
        # Filter by category (including children)
        category_id = self.request.query_params.get('category')
        if category_id:
            from django.db.models import Q
            # Get category and all its children
            category = ServiceCategory.objects.get(id=category_id)
            categories = [category_id]
            children = category.children.all()
            categories.extend([c.id for c in children])
            queryset = queryset.filter(category_id__in=categories)
        
        return queryset.prefetch_related('required_materials')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsBranchAdmin()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def add_material(self, request, pk=None):
        """
        Add required material to service
        """
        service = self.get_object()
        serializer = ServiceMaterialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(service=service)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PriceListViewSet(viewsets.ModelViewSet):
    """
    Price list CRUD
    """
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['start_date', 'name']
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.query_params.get('branch')
        
        queryset = PriceList.objects.filter(organization=user.organization)
        
        if branch_id:
            # Get pricelists for specific branch or organization-wide
            from django.db.models import Q
            queryset = queryset.filter(
                Q(branch_id=branch_id) | Q(branch__isnull=True)
            )
        
        return queryset.prefetch_related('items__service')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PriceListListSerializer
        return PriceListSerializer
    
    @action(detail=True, methods=['post'])
    def add_items(self, request, pk=None):
        """
        Add multiple price items to price list
        """
        pricelist = self.get_object()
        items_data = request.data.get('items', [])
        
        created_items = []
        for item_data in items_data:
            item_data['pricelist'] = pricelist.id
            serializer = PriceItemSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                created_items.append(serializer.data)
        
        return Response({
            'created': len(created_items),
            'items': created_items
        }, status=status.HTTP_201_CREATED)


class PriceItemViewSet(viewsets.ModelViewSet):
    """
    Price item CRUD
    """
    queryset = PriceItem.objects.all()
    serializer_class = PriceItemSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_queryset(self):
        user = self.request.user
        pricelist_id = self.request.query_params.get('pricelist')
        
        queryset = PriceItem.objects.filter(
            pricelist__organization=user.organization
        )
        
        if pricelist_id:
            queryset = queryset.filter(pricelist_id=pricelist_id)
        
        return queryset.select_related('service', 'pricelist')


class ICDCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ICD code lookup (read-only)
    """
    queryset = ICDCode.objects.filter(is_active=True)
    serializer_class = ICDCodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name', 'name_ru']
    pagination_class = None  # Disable pagination for ICD lookup
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by code prefix
        code_prefix = self.request.query_params.get('code_prefix')
        if code_prefix:
            queryset = queryset.filter(code__startswith=code_prefix)
        
        # Limit results
        return queryset[:100]

