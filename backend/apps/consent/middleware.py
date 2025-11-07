"""
Middleware for grant-based access control
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone
from .models import AccessGrant


class GrantAccessMiddleware(MiddlewareMixin):
    """
    Middleware to check and validate grant access for external patient data
    
    Checks for X-Access-Grant-ID header and validates grant
    Adds grant to request if valid
    """
    
    def process_request(self, request):
        """Process incoming request"""
        # Skip for unauthenticated requests
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Check for grant ID in header
        grant_id = request.headers.get('X-Access-Grant-ID')
        
        if not grant_id:
            # No grant ID provided - continue normally
            request.active_grant = None
            return None
        
        try:
            # Validate and get grant
            grant = AccessGrant.objects.select_related('patient', 'grantee_org').get(
                id=grant_id,
                grantee_org=request.user.organization,
                revoked_at__isnull=True
            )
            
            # Check if grant is active
            if not grant.is_active():
                return JsonResponse({
                    'error': 'Grant has expired or is not yet valid',
                    'grant_id': str(grant_id),
                    'valid_from': grant.valid_from.isoformat(),
                    'valid_to': grant.valid_to.isoformat()
                }, status=403)
            
            # Attach grant to request
            request.active_grant = grant
            
            # Track access (only for non-OPTIONS requests)
            if request.method != 'OPTIONS':
                grant.track_access()
            
        except AccessGrant.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid or inaccessible grant',
                'grant_id': str(grant_id)
            }, status=403)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error validating grant: {e}')
            return JsonResponse({
                'error': 'Error validating grant',
                'detail': str(e)
            }, status=500)
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response"""
        # Add grant info to response headers if grant was used
        if hasattr(request, 'active_grant') and request.active_grant:
            response['X-Grant-Valid-Until'] = request.active_grant.valid_to.isoformat()
            response['X-Grant-Scopes'] = ','.join(request.active_grant.scopes)
        
        return response


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all patient data access for audit trail
    """
    
    # Paths to audit
    AUDIT_PATHS = [
        '/api/v1/patients/',
        '/api/v1/visits/',
        '/api/v1/ehr/',
    ]
    
    def process_response(self, request, response):
        """Log access after response"""
        # Only log for authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Only log successful requests (2xx status codes)
        if not (200 <= response.status_code < 300):
            return response
        
        # Check if request path should be audited
        should_audit = any(request.path.startswith(path) for path in self.AUDIT_PATHS)
        
        if not should_audit:
            return response
        
        # Determine action based on method
        action_map = {
            'GET': 'read',
            'POST': 'write',
            'PUT': 'write',
            'PATCH': 'write',
            'DELETE': 'write',
        }
        action = action_map.get(request.method, 'other')
        
        # Try to extract patient ID from request/response
        patient_id = self._extract_patient_id(request, response)
        
        if not patient_id:
            return response
        
        # Create audit log asynchronously
        try:
            from .tasks import create_audit_log_async
            
            create_audit_log_async.delay(
                user_id=request.user.id,
                organization_id=request.user.organization.id,
                patient_id=patient_id,
                action=action,
                object_type=self._get_object_type(request.path),
                object_id=self._extract_object_id(request.path),
                grant_id=str(request.active_grant.id) if hasattr(request, 'active_grant') and request.active_grant else None,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                }
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error creating audit log: {e}')
        
        return response
    
    def _extract_patient_id(self, request, response):
        """Extract patient ID from request or response"""
        # Try to get from request
        if hasattr(request, 'active_grant') and request.active_grant:
            return request.active_grant.patient.id
        
        # Try to parse from URL
        import re
        match = re.search(r'/patients/(\d+)/', request.path)
        if match:
            return int(match.group(1))
        
        # Try to get from request data
        if hasattr(request, 'data') and isinstance(request.data, dict):
            if 'patient' in request.data:
                return request.data['patient']
            if 'patient_id' in request.data:
                return request.data['patient_id']
        
        return None
    
    def _get_object_type(self, path):
        """Get object type from path"""
        if '/patients/' in path:
            return 'Patient'
        elif '/visits/' in path:
            return 'Visit'
        elif '/ehr/' in path:
            return 'EHRRecord'
        return 'Unknown'
    
    def _extract_object_id(self, path):
        """Extract object ID from path"""
        import re
        # Match patterns like /visits/123/ or /patients/456/
        match = re.search(r'/(\w+)/(\d+)/', path)
        if match:
            return match.group(2)
        return None
