from django.shortcuts import render
from .models import Transacao

def index(request):
    # Busca todas as transações do banco
    transacoes = Transacao.objects.all()
    
    # Prepara o pacote de dados para enviar ao HTML
    contexto = {
        'transacoes': transacoes
    }
    
    # Renderiza o arquivo html enviando o contexto
    return render(request, 'financas/index.html', contexto)