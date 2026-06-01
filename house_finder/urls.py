from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_root),                     
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('listings.urls')),
    path('api/v1/', include('bookings.urls')),
    path('api/v1/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)