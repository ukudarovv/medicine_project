from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    MeView,
    Enable2FAView,
    Verify2FAView,
    Disable2FAView
)

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('me', MeView.as_view(), name='me'),
    path('2fa/enable', Enable2FAView.as_view(), name='2fa_enable'),
    path('2fa/verify', Verify2FAView.as_view(), name='2fa_verify'),
    path('2fa/disable', Disable2FAView.as_view(), name='2fa_disable'),
]
