"""
URL configuration for Medicine ERP project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('apps.core.urls')),
        path('org/', include('apps.org.urls')),
        path('staff/', include('apps.staff.urls')),
        path('patients/', include('apps.patients.urls')),
        path('services/', include('apps.services.urls')),
        path('calendar/', include('apps.calendar.urls')),
        path('visits/', include('apps.visits.urls')),
        path('billing/', include('apps.billing.urls')),
        path('warehouse/', include('apps.warehouse.urls')),
        path('comms/', include('apps.comms.urls')),
        path('reports/', include('apps.reports.urls')),
    ])),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

