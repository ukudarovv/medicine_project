from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, MessageLogViewSet

router = DefaultRouter()
router.register('templates', TemplateViewSet)
router.register('messages', MessageLogViewSet, basename='message')

urlpatterns = [path('', include(router.urls))]
