from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({'status': 'ok'})


def readiness(_request):
    try:
        connections['default'].cursor().execute('SELECT 1')
    except OperationalError:
        return JsonResponse({'status': 'error', 'database': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok', 'database': 'available'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health, name='health'),
    path('api/health/ready/', readiness, name='readiness'),
    path('api/', include('apps.portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
