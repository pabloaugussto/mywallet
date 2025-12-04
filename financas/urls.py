from django.urls import path
from . import views

urlpatterns = [
    # Quando acessar a raiz, chama a função 'index' na views
    path('', views.index, name='index'),
]