from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# 1. MetaFinanceira (No topo)
class MetaFinanceira(models.Model):
    nome = models.CharField(max_length=50)
    valor_alvo = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} (Alvo: {self.valor_alvo})"

# 2. Categoria e MetaCategoria
class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=1, choices=[('R', 'Receita'), ('D', 'Despesa')])
    def __str__(self): return self.nome

class MetaCategoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    valor_limite = models.DecimalField(max_digits=10, decimal_places=2)

# 3. Investimento (Separado)
class Investimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    simbolo = models.CharField(max_length=20)
    quantidade = models.DecimalField(max_digits=15, decimal_places=2)
    ultimo_deposito = models.DateField(null=True, blank=True)
    def __str__(self): return f"{self.simbolo} ({self.quantidade})"

# 4. Transacao (No final, usando MetaFinanceira)
class Transacao(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    data = models.DateField(default=datetime.now)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacoes = models.TextField(blank=True, null=True)
    comprovante = models.FileField(upload_to='comprovantes/', blank=True, null=True)
    moeda = models.CharField(max_length=3, default='BRL')
    
    # Campo correto de ligação com a Meta
    meta_relacionada = models.ForeignKey(MetaFinanceira, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes')

    def __str__(self):
        return self.descricao