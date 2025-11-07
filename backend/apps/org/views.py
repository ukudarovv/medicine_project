from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsOwner, IsBranchAdmin, IsSuperAdmin
from apps.core.models import User
from .models import Organization, Branch, Room, Resource, Settings, ClinicInfo
from .serializers import (
    OrganizationSerializer,
    BranchSerializer,
    BranchListSerializer,
    RoomSerializer,
    ResourceSerializer,
    SettingsSerializer,
    ClinicInfoSerializer,
    OrganizationUserSerializer,
    OrganizationUserCreateSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization CRUD
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Super admins can do everything, owners can only view their org
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        # Super admins can see all organizations
        if self.request.user.is_superuser:
            return Organization.objects.all()
        
        # Users can only see their own organization
        if self.request.user.organization:
            return Organization.objects.filter(id=self.request.user.organization.id)
        return Organization.objects.none()
    
    @action(detail=True, methods=['get', 'post'], url_path='users')
    def users(self, request, pk=None):
        """
        Get or create users for an organization
        Only superadmins and organization owners can access
        """
        organization = self.get_object()
        
        # Check permissions
        if not request.user.is_superuser and request.user.organization != organization:
            return Response(
                {'detail': 'You do not have permission to access this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            users = User.objects.filter(organization=organization)
            serializer = OrganizationUserSerializer(users, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Only owner or superadmin can create users
            if request.user.role != 'owner' and not request.user.is_superuser:
                return Response(
                    {'detail': 'Only organization owners can create users.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = OrganizationUserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save(organization=organization)
                return Response(
                    OrganizationUserSerializer(user).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchViewSet(viewsets.ModelViewSet):
    """
    Branch CRUD
    """
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only require branch membership for create/update/delete, not for list/retrieve
        """
        if self.action in ['list', 'retrieve', 'my_branches']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsBranchMember()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Superuser can see all branches
        if user.is_superuser:
            return Branch.objects.all()
        
        # Owner can see all branches in organization
        if user.role == 'owner' and user.organization:
            return Branch.objects.filter(organization=user.organization)
        
        # Others can only see branches they have access to
        from apps.core.models import UserBranchAccess
        branch_ids = UserBranchAccess.objects.filter(
            user=user
        ).values_list('branch_id', flat=True)
        
        return Branch.objects.filter(id__in=branch_ids)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer
    
    @action(detail=False, methods=['get'])
    def my_branches(self, request):
        """
        Get branches accessible by current user
        """
        branches = self.get_queryset()
        serializer = BranchListSerializer(branches, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    """
    Room CRUD
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.query_params.get('branch')
        
        queryset = Room.objects.all()
        
        # Filter by branch if provided
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by user's organization
        if user.organization:
            queryset = queryset.filter(branch__organization=user.organization)
        
        return queryset


class ResourceViewSet(viewsets.ModelViewSet):
    """
    Resource CRUD
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.query_params.get('branch')
        
        queryset = Resource.objects.all()
        
        # Filter by branch if provided
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Filter by user's organization
        if user.organization:
            queryset = queryset.filter(branch__organization=user.organization)
        
        return queryset


class SettingsViewSet(viewsets.ModelViewSet):
    """
    Settings CRUD
    """
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.branch_id
        
        queryset = Settings.objects.all()
        
        # Filter by organization
        if user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        # Filter by branch if provided
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        return queryset
    
    @action(detail=False, methods=['get', 'patch'])
    def bulk(self, request):
        """
        Get or update multiple settings at once
        """
        if request.method == 'GET':
            settings = self.get_queryset()
            serializer = self.get_serializer(settings, many=True)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            # Update multiple settings
            settings_data = request.data.get('settings', [])
            
            for setting_data in settings_data:
                key = setting_data.get('key')
                value = setting_data.get('value')
                
                if key and value is not None:
                    Settings.objects.update_or_create(
                        organization=request.user.organization,
                        branch_id=request.branch_id,
                        key=key,
                        defaults={'value': value}
                    )
            
            return Response({'message': 'Settings updated'})


class ClinicInfoView(generics.RetrieveUpdateAPIView):
    """
    Clinic information view
    GET/PATCH /api/v1/org/clinic-info
    """
    serializer_class = ClinicInfoSerializer
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    
    def get_object(self):
        user = self.request.user
        
        if not user.organization:
            from rest_framework.exceptions import NotFound
            raise NotFound('User is not associated with any organization')
        
        # Get or create clinic info
        clinic_info, created = ClinicInfo.objects.get_or_create(
            organization=user.organization
        )
        
        return clinic_info


class OrganizationUserViewSet(viewsets.ModelViewSet):
    """
    User management for organizations
    """
    queryset = User.objects.all()
    serializer_class = OrganizationUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter users by organization
        """
        user = self.request.user
        org_id = self.request.query_params.get('organization')
        
        # Superadmin can see all users
        if user.is_superuser:
            if org_id:
                return User.objects.filter(organization_id=org_id)
            return User.objects.all()
        
        # Owners can only see users in their organization
        if user.role == 'owner' and user.organization:
            return User.objects.filter(organization=user.organization)
        
        return User.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationUserCreateSerializer
        return OrganizationUserSerializer
    
    def perform_create(self, serializer):
        """
        Create user in the organization
        """
        user = self.request.user
        org_id = self.request.data.get('organization_id')
        
        # Validate permissions
        if user.is_superuser:
            if org_id:
                organization = Organization.objects.get(id=org_id)
            else:
                raise serializers.ValidationError({'organization_id': 'Required for superadmin'})
        elif user.role == 'owner':
            organization = user.organization
        else:
            raise serializers.ValidationError({'detail': 'Permission denied'})
        
        serializer.save(organization=organization)
    
    def perform_update(self, serializer):
        """
        Update user - only allow certain fields
        """
        user = self.request.user
        instance = self.get_object()
        
        # Check permissions
        if not user.is_superuser and user.organization != instance.organization:
            raise serializers.ValidationError({'detail': 'Permission denied'})
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete user
        """
        user = self.request.user
        
        # Check permissions
        if not user.is_superuser and user.organization != instance.organization:
            raise serializers.ValidationError({'detail': 'Permission denied'})
        
        # Don't allow deleting yourself
        if instance.id == user.id:
            raise serializers.ValidationError({'detail': 'Cannot delete yourself'})
        
        instance.delete()

