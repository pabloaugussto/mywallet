from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    # Opções para o campo 'tipo' (tuplas: valor no banco, valor na tela)
    TIPO_CHOICES = (
        ('R', 'Receita'),
        ('D', 'Despesa'),
    )

    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    # auto_now_add=True preenche a data automaticamente na criação
    dt_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Transacao(models.Model):
    descricao = models.CharField(max_length=100)
    # DecimalField é OBRIGATÓRIO para dinheiro (float gera erros de arredondamento)
    valor = models.DecimalField(max_digits=9, decimal_places=2)
    data = models.DateField()
    observacoes = models.TextField(null=True, blank=True)
    
    # upload_to define a subpasta dentro da pasta 'media'
    comprovante = models.ImageField(upload_to='comprovantes/', null=True, blank=True)

    # RELACIONAMENTOS (O "fortalecimento" da base está aqui):
    
    # 1. Uma transação pertence a UMA categoria
    # on_delete=models.SET_NULL: se apagar a categoria, a transação fica sem categoria (não apaga o dinheiro)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)

    # 2. Uma transação pertence a UM usuário (para seu app ser multi-usuário)
    # on_delete=models.CASCADE: se apagar o usuário, apaga todas as transações dele
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    OPCOES_MOEDA = (
        ('BRL', 'Real (R$)'),
        ('USD', 'Dólar (US$)'),
    )
    moeda = models.CharField(max_length=3, choices=OPCOES_MOEDA, default='BRL')

    def __str__(self):
        return self.descricao
    


# A classe Investimento deve ficar FORA da Transacao (alinhada à esquerda)
class Investimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    simbolo = models.CharField(max_length=20) 
    quantidade = models.DecimalField(max_digits=15, decimal_places=8) 

    def __str__(self):
        return f"{self.simbolo} ({self.quantidade})"