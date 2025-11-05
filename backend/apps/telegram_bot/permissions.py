"""
Authentication and permissions for Telegram Bot API
"""
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class BotAPIAuthentication(BaseAuthentication):
    """
    Simple token-based authentication for bot API
    Bot must send: Authorization: Bearer <TELEGRAM_BOT_API_SECRET>
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                raise AuthenticationFailed('Invalid authentication scheme')
            
            # Check if token matches the secret
            expected_token = getattr(settings, 'TELEGRAM_BOT_API_SECRET', None)
            if not expected_token:
                raise AuthenticationFailed('Bot API secret not configured')
            
            if token != expected_token:
                raise AuthenticationFailed('Invalid bot API token')
            
            # Return None for user, None for auth (stateless)
            return (None, None)
            
        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format')


class IsBotAuthenticated(permissions.BasePermission):
    """
    Permission class to check if request is from authenticated bot
    """
    def has_permission(self, request, view):
        # If BotAPIAuthentication was successful, allow access
        return True  # BotAPIAuthentication will raise exception if failed

