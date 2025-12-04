from django.urls import path
from . import views

urlpatterns = [
    # Quando acessar a raiz, chama a função 'index' na views
    path('', views.index, name='index'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('nova/', views.nova_transacao, name='nova_transacao'), # Nova linha
]