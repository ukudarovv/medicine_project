from rest_framework import permissions


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


class CanAccessPatient(permissions.BasePermission):
    """
    Object-level permission to check if user can access a patient
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner has access to all patients in organization
        if request.user.role == 'owner':
            return obj.organization == request.user.organization
        
        # Check if patient is in a branch the user has access to
        branch_id = request.branch_id
        if not branch_id:
            return False
        
        # Patient belongs to the organization
        return obj.organization == request.user.organization


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

