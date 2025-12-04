import requests
import json
from decimal import Decimal 
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Transacao
from .forms import TransacaoForm

def index(request):
    # 1. Buscar cotação (padrão 6.00 se der erro)
    cotacao_dolar = 6.00 
    
    try:
        response = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=5)
        if response.status_code == 200:
            data = response.json()
            cotacao_dolar = float(data['USDBRL']['bid']) # Forçamos ser float aqui
    except:
        pass 

    # --- CÁLCULO DOS TOTAIS ---
    # Convertendo os valores do banco (que são Decimal) para float imediatamente
    receitas_brl = float(Transacao.objects.filter(categoria__tipo='R', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    receitas_usd = float(Transacao.objects.filter(categoria__tipo='R', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    
    # Agora float * float não dá erro nunca
    total_receitas = receitas_brl + (receitas_usd * cotacao_dolar)

    despesas_brl = float(Transacao.objects.filter(categoria__tipo='D', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    despesas_usd = float(Transacao.objects.filter(categoria__tipo='D', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    
    total_despesas = despesas_brl + (despesas_usd * cotacao_dolar)

    saldo = total_receitas - total_despesas

    # --- DADOS DA TABELA ---
    transacoes = Transacao.objects.all().order_by('-data')

    # --- DADOS DO GRÁFICO ---
    gastos_por_categoria = Transacao.objects.values('categoria__nome').annotate(total=Sum('valor'))
    
    # Substitua a linha 40 original por esta:
    lista_categorias = [f"{x['categoria__nome']} - R$ {(x['total'] or 0):.2f}" for x in gastos_por_categoria]
    lista_valores = [float(x['total'] or 0) for x in gastos_por_categoria]

    context = {
        'receitas': total_receitas,
        'despesas': total_despesas,
        'saldo': saldo,
        'transacoes': transacoes,
        'cotacao_atual': cotacao_dolar,
        'grafico_labels': json.dumps(lista_categorias), 
        'grafico_data': json.dumps(lista_valores),
    }

    return render(request, 'financas/index.html', context)

# --- OUTRAS FUNÇÕES ---

def nova_transacao(request):
    form = TransacaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        transacao = form.save(commit=False)
        transacao.usuario = request.user 
        transacao.save()
        return redirect('index')
    return render(request, 'financas/form.html', {'form': form})

def editar_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    form = TransacaoForm(request.POST or None, request.FILES or None, instance=transacao)
    if form.is_valid():
        form.save()
        return redirect('index')
    return render(request, 'financas/form.html', {'form': form})

def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    transacao.delete()
    return redirect('index')