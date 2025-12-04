import requests
from decimal import Decimal # <--- IMPORTANTE: Adicionamos isso aqui!
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Transacao
from .forms import TransacaoForm

# --- DASHBOARD (Página Inicial) ---
def index(request):
    # 1. Buscar a cotação do Dólar em tempo real
    # Usamos Decimal('6.00') para garantir que o padrão também seja Decimal
    cotacao_dolar = Decimal('6.00') 
    
    try:
        response = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Convertendo o valor da API (string) diretamente para Decimal
            cotacao_dolar = Decimal(data['USDBRL']['bid'])
    except:
        pass # Mantém o 6.00 se der erro

    # --- CÁLCULO DAS RECEITAS ---
    receitas_brl = Transacao.objects.filter(categoria__tipo='R', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    receitas_usd = Transacao.objects.filter(categoria__tipo='R', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    
    # Agora a multiplicação funciona porque ambos são Decimal
    total_receitas = receitas_brl + (receitas_usd * cotacao_dolar)

    # --- CÁLCULO DAS DESPESAS ---
    despesas_brl = Transacao.objects.filter(categoria__tipo='D', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    despesas_usd = Transacao.objects.filter(categoria__tipo='D', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    
    total_despesas = despesas_brl + (despesas_usd * cotacao_dolar)

    # --- SALDO ---
    saldo = total_receitas - total_despesas

    # Busca as transações para a tabela
    transacoes = Transacao.objects.all().order_by('-data')

    context = {
        'receitas': total_receitas,
        'despesas': total_despesas,
        'saldo': saldo,
        'transacoes': transacoes,
        'cotacao_atual': cotacao_dolar
    }

    return render(request, 'financas/index.html', context)

# --- CRIAR NOVA TRANSAÇÃO ---
def nova_transacao(request):
    form = TransacaoForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        form.save()
        return redirect('index')
        
    return render(request, 'financas/form.html', {'form': form})

# --- EDITAR TRANSAÇÃO ---
def editar_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    form = TransacaoForm(request.POST or None, request.FILES or None, instance=transacao)
    
    if form.is_valid():
        form.save()
        return redirect('index')
        
    return render(request, 'financas/form.html', {'form': form})

# --- EXCLUIR TRANSAÇÃO ---
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    transacao.delete()
    return redirect('index')