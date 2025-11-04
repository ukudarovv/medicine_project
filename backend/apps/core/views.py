from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import (
    LoginSerializer,
    UserSerializer,
    Enable2FASerializer,
    Verify2FASerializer,
    Disable2FASerializer
)


class LoginView(views.APIView):
    """
    Login endpoint
    POST /api/v1/auth/login
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class MeView(generics.RetrieveAPIView):
    """
    Get current user profile
    GET /api/v1/auth/me
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class Enable2FAView(views.APIView):
    """
    Generate 2FA QR code
    POST /api/v1/auth/2fa/enable
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = Enable2FASerializer(
            data={},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class Verify2FAView(views.APIView):
    """
    Verify 2FA token and enable it
    POST /api/v1/auth/2fa/verify
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = Verify2FASerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class Disable2FAView(views.APIView):
    """
    Disable 2FA
    POST /api/v1/auth/2fa/disable
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = Disable2FASerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)

