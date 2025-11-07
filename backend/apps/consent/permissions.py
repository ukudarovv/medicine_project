"""
Permissions for consent system
"""
from rest_framework import permissions


class CanRequestAccess(permissions.BasePermission):
    """
    Permission to create access requests
    Allowed roles: doctor, registrar, branch_admin, owner
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check role
        allowed_roles = ['doctor', 'registrar', 'branch_admin', 'owner']
        return request.user.role in allowed_roles


class CanViewExternalRecords(permissions.BasePermission):
    """
    Permission to view external records (from other organizations)
    Requires active AccessGrant
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # This will be checked in the view/queryset level
        return True


class CanWriteExternalRecords(permissions.BasePermission):
    """
    Permission to write to external patient records
    Requires active AccessGrant with write_records scope
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # This will be checked in the view level with scope verification
        return True


class CanViewSensitiveData(permissions.BasePermission):
    """
    Permission to view sensitive data (full IIN, etc.)
    Allowed roles: owner, branch_admin
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check role
        allowed_roles = ['owner', 'branch_admin']
        return request.user.role in allowed_roles


class HasActiveGrant(permissions.BasePermission):
    """
    Permission to access patient data via active grant
    Checks if user's organization has an active grant for the patient
    """
    message = 'Active grant required to access this patient\'s data'
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user's org has active grant for the patient
        Works with objects that have a 'patient' attribute
        """
        from .models import AccessGrant
        from django.utils import timezone
        
        # Get patient from object
        patient = None
        if hasattr(obj, 'patient'):
            patient = obj.patient
        elif hasattr(obj, 'appointment') and hasattr(obj.appointment, 'patient'):
            patient = obj.appointment.patient
        
        if not patient:
            return False
        
        # Check if same organization (allow own data)
        if patient.has_organization(request.user.organization):
            return True
        
        # Check for active grant
        now = timezone.now()
        grant = AccessGrant.objects.filter(
            patient=patient,
            grantee_org=request.user.organization,
            valid_from__lte=now,
            valid_to__gte=now,
            revoked_at__isnull=True
        ).first()
        
        if not grant:
            return False
        
        # Check scope based on request method
        if request.method in permissions.SAFE_METHODS:
            # Read operations - need read_records or read_summary
            required_scopes = ['read_records', 'read_summary']
        else:
            # Write operations - need write_records
            required_scopes = ['write_records']
        
        # Check if grant has at least one required scope
        has_required_scope = any(scope in grant.scopes for scope in required_scopes)
        
        if not has_required_scope:
            self.message = f'Grant does not include required scope: {required_scopes}'
            return False
        
        # Track access
        grant.track_access()
        
        return True


class HasGrantWithScope(permissions.BasePermission):
    """
    Permission that checks for specific scopes in grant
    Usage: Add required_scopes attribute to view
    """
    message = 'Required scope not found in grant'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        from .models import AccessGrant
        from django.utils import timezone
        
        # Get required scopes from view
        required_scopes = getattr(view, 'required_scopes', [])
        if not required_scopes:
            return True  # No specific scopes required
        
        # Get patient
        patient = None
        if hasattr(obj, 'patient'):
            patient = obj.patient
        elif hasattr(obj, 'appointment') and hasattr(obj.appointment, 'patient'):
            patient = obj.appointment.patient
        
        if not patient:
            return False
        
        # Same org always allowed
        if patient.has_organization(request.user.organization):
            return True
        
        # Check grant with specific scopes
        now = timezone.now()
        grant = AccessGrant.objects.filter(
            patient=patient,
            grantee_org=request.user.organization,
            valid_from__lte=now,
            valid_to__gte=now,
            revoked_at__isnull=True
        ).first()
        
        if not grant:
            self.message = 'No active grant found'
            return False
        
        # Check if all required scopes are in grant
        has_all_scopes = all(scope in grant.scopes for scope in required_scopes)
        
        if not has_all_scopes:
            missing = [s for s in required_scopes if s not in grant.scopes]
            self.message = f'Missing required scopes: {missing}'
            return False
        
        grant.track_access()
        return True
