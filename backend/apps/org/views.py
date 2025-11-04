from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsOwner, IsBranchAdmin
from .models import Organization, Branch, Room, Resource, Settings, ClinicInfo
from .serializers import (
    OrganizationSerializer,
    BranchSerializer,
    BranchListSerializer,
    RoomSerializer,
    ResourceSerializer,
    SettingsSerializer,
    ClinicInfoSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization CRUD
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        # Users can only see their own organization
        if self.request.user.organization:
            return Organization.objects.filter(id=self.request.user.organization.id)
        return Organization.objects.none()


class BranchViewSet(viewsets.ModelViewSet):
    """
    Branch CRUD
    """
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        
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
            return None
        
        # Get or create clinic info
        clinic_info, created = ClinicInfo.objects.get_or_create(
            organization=user.organization
        )
        
        return clinic_info

