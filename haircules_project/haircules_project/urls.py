from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    path('face/', include('face_analysis.urls')),
    path('accounts/', include('accounts.urls')),
]

# TAMBAH INI UNTUK MEDIA FILES!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)