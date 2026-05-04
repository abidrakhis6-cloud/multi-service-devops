from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# Health check endpoint for CI/CD smoke tests
def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'multiserve'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.api_urls')),
    path('api/v1/auth/', include('accounts.urls')),  # Auth avancée (OTP, OAuth)
    path('health/', health_check, name='health'),
    path('', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)