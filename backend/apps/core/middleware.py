from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant logic based on X-Branch-Id header
    """
    
    def process_request(self, request):
        # Get branch ID from header
        branch_id = request.headers.get('X-Branch-Id')
        
        # Attach branch ID to request for use in views
        request.branch_id = branch_id
        
        # If user is authenticated and branch_id is provided, validate access
        if request.user.is_authenticated and branch_id:
            # Check if user has access to this branch
            from apps.core.models import UserBranchAccess
            
            has_access = UserBranchAccess.objects.filter(
                user=request.user,
                branch_id=branch_id
            ).exists()
            
            # Owner role has access to all branches
            if not has_access and request.user.role != 'owner':
                # Skip check for certain endpoints (like /me, /branches)
                if not any(path in request.path for path in ['/auth/me', '/org/branches', '/auth/']):
                    return JsonResponse(
                        {'error': 'Access denied to this branch'},
                        status=403
                    )
        
        return None

