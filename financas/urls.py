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

urlpatterns = [
    path('', views.index, name='index'),
    path('nova/', views.nova_transacao, name='nova_transacao'),
    
    # <int:pk> significa que o Django espera um número inteiro e vai chamá-lo de 'pk'
    path('editar/<int:pk>/', views.editar_transacao, name='editar_transacao'),
    path('excluir/<int:pk>/', views.excluir_transacao, name='excluir_transacao'),
    path('investimento/editar/<int:pk>/', views.editar_investimento, name='editar_investimento'),
    path('webhook/', views.bot_whatsapp, name='bot_whatsapp'),
]


