from django.contrib import admin
# AQUI ESTAVA O ERRO: Adicionamos o ', include'
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adicione esta linha para ter login/logout prontos:
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('financas.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)