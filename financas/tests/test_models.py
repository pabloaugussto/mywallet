import pytest
from financas.models import Transacao, Categoria, Investimento
from django.contrib.auth.models import User
from datetime import date

# Essa marcação permite que o teste acesse o banco de dados
@pytest.mark.django_db
def test_criar_categoria():
    """Testa se consegue criar uma categoria e se o __str__ dela retorna o nome"""
    cat = Categoria.objects.create(nome="Lazer", tipo="D")
    assert cat.nome == "Lazer"
    assert str(cat) == "Lazer"

@pytest.mark.django_db
def test_criar_investimento():
    """Testa se o modelo de Investimento salva as casas decimais corretamente"""
    user = User.objects.create(username="teste")
    inv = Investimento.objects.create(
        usuario=user,
        simbolo="MPAGO",
        quantidade=1500.50
    )
    assert inv.simbolo == "MPAGO"
    assert inv.quantidade == 1500.50
    assert str(inv) == "MPAGO (1500.5)"