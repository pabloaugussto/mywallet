import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from financas.models import Investimento

@pytest.mark.django_db
def test_acesso_dashboard_sem_login(client):
    """Quem não está logado deve ser redirecionado para o login (do Admin)"""
    url = reverse('index')
    response = client.get(url)
    assert response.status_code == 302
    # CORREÇÃO: Verificamos se redireciona para o /admin/login/
    assert '/admin/login/' in response.url

@pytest.mark.django_db
def test_acesso_dashboard_com_login(client):
    """Usuário logado deve ver a dashboard (Status 200)"""
    # 1. Cria usuário e força o login
    user = User.objects.create_user(username='usuario_teste', password='123')
    client.force_login(user)

    # 2. Acessa a dashboard
    url = reverse('index')
    response = client.get(url)

    # 3. Verifica se deu certo
    assert response.status_code == 200
    # Verifica se o texto "MyWallet" aparece no HTML retornado
    assert "MyWallet" in response.content.decode('utf-8')

@pytest.mark.django_db
def test_investimento_aparece_na_dashboard(client):
    """Testa se um investimento criado aparece no HTML da dashboard"""
    user = User.objects.create_user(username='investidor', password='123')
    Investimento.objects.create(usuario=user, simbolo="PLUXEE", quantidade=500)
    
    client.force_login(user)
    response = client.get(reverse('index'))
    
    conteudo = response.content.decode('utf-8')
    assert "PLUXEE" in conteudo
    assert "500" in conteudo