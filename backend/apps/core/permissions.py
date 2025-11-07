from rest_framework import permissions


class OrganizationFilterMixin:
    """
    Mixin to filter querysets by organization.
    Superusers see all, users with organization see their org, users without org see nothing.
    """
    
    def filter_by_organization(self, queryset, field='organization', many_to_many=False):
        """
        Filter queryset by organization field.
        
        Args:
            queryset: Base queryset to filter
            field: Field name to filter on (default 'organization')
            many_to_many: Whether the field is ManyToMany (default False)
        
        Returns:
            Filtered queryset
        """
        user = self.request.user
        
        if user.is_superuser:
            return queryset
        elif user.organization:
            if many_to_many:
                # For ManyToMany fields (e.g., Patient.organizations)
                filter_kwargs = {f'{field}': user.organization}
            else:
                # For ForeignKey fields
                filter_kwargs = {field: user.organization}
            return queryset.filter(**filter_kwargs)
        else:
            return queryset.none()


class IsBranchMember(permissions.BasePermission):
    """
    Permission to check if user has access to the branch
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Owner has access to everything
        if request.user.role == 'owner':
            return True
        
        # Check branch access
        branch_id = request.branch_id
        if not branch_id:
            return False
        
        from apps.core.models import UserBranchAccess
        return UserBranchAccess.objects.filter(
            user=request.user,
            branch_id=branch_id
        ).exists()


class IsOwner(permissions.BasePermission):
    """
    Permission for organization owners only
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'owner'


class IsBranchAdmin(permissions.BasePermission):
    """
    Permission for branch admins and owners
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['owner', 'branch_admin']
        )


class IsDoctor(permissions.BasePermission):
    """
    Permission for doctors (and admins)
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['owner', 'branch_admin', 'doctor']
        )


class IsCashier(permissions.BasePermission):
    """
    Permission for cashiers (and admins)
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['owner', 'branch_admin', 'cashier']
        )


class IsRegistrar(permissions.BasePermission):
    """
    Permission for registrars (and admins)
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['owner', 'branch_admin', 'registrar']
        )


class IsWarehouse(permissions.BasePermission):
    """
    Permission for warehouse staff (and admins)
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['owner', 'branch_admin', 'warehouse']
        )


class IsMarketer(permissions.BasePermission):
    """
    Permission for marketers (and admins)
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['owner', 'branch_admin', 'marketer']
        )


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission for super admins only (Django superuser)
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class CanAccessPatient(permissions.BasePermission):
    """
    Object-level permission to check if user can access a patient
    """
    
    def has_object_permission(self, request, view, obj):
        # Superuser has access to all patients
        if request.user.is_superuser:
            return True
        
        # Check if user has organization
        if not request.user.organization:
            return False
        
        # Check if patient belongs to user's organization
        return obj.has_organization(request.user.organization)


class CanAccessVisit(permissions.BasePermission):
    """
    Object-level permission for visits
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner has full access
        if request.user.role == 'owner':
            return True
        
        # Doctor can only access their own visits
        if request.user.role == 'doctor':
            # Check if this doctor is assigned to the appointment
            return obj.appointment.employee.user == request.user
        
        # Branch staff can access visits in their branch
        branch_id = request.branch_id
        if not branch_id:
            return False
        
        return obj.appointment.branch_id == int(branch_id)

