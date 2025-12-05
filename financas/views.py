from django.contrib import messages
import requests
import json
from decimal import Decimal 
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Transacao
from .forms import TransacaoForm

@login_required
def index(request):
    # --- 1. Filtros de Data ---
    hoje = datetime.now()
    try:
        mes_atual = int(request.GET.get('mes', hoje.month))
        ano_atual = int(request.GET.get('ano', hoje.year))
    except ValueError:
        mes_atual = hoje.month
        ano_atual = hoje.year

    # Filtra as transações apenas deste mês/ano
    transacoes_do_mes = Transacao.objects.filter(
        data__month=mes_atual, 
        data__year=ano_atual,
        usuario=request.user  # Garante que só vê as suas contas
    )

    # --- 2. Cotação do Dólar ---
    cotacao_dolar = 6.00 
    try:
        response = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=2)
        if response.status_code == 200:
            data = response.json()
            cotacao_dolar = float(data['USDBRL']['bid'])
    except:
        pass 

    # --- 3. Totais (Receita vs Despesa) ---
    # Soma Receitas (R e USD convertidos)
    receitas_brl = float(transacoes_do_mes.filter(categoria__tipo='R', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    receitas_usd = float(transacoes_do_mes.filter(categoria__tipo='R', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    total_receitas = receitas_brl + (receitas_usd * cotacao_dolar)

    # Soma Despesas (R e USD convertidos)
    despesas_brl = float(transacoes_do_mes.filter(categoria__tipo='D', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    despesas_usd = float(transacoes_do_mes.filter(categoria__tipo='D', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    total_despesas = despesas_brl + (despesas_usd * cotacao_dolar)

    saldo = total_receitas - total_despesas

    # --- 4. Gráfico e Tabela ---
    transacoes = transacoes_do_mes.order_by('-data')
    
    dados_grafico = {} 
    
    # LÓGICA DO GRÁFICO (Convertendo Dólar e Filtrando Despesa)
    for t in transacoes_do_mes:
        if t.categoria.tipo == 'D':  # Só entra se for Despesa
            valor_real = float(t.valor)
            
            if t.moeda == 'USD':     # Só converte se for Dólar
                valor_real = valor_real * cotacao_dolar
            
            nome = t.categoria.nome
            # Soma no acumulador
            dados_grafico[nome] = dados_grafico.get(nome, 0) + valor_real

    # Transforma em listas para o HTML
    lista_categorias = []
    lista_valores = []
    
    for nome, valor in dados_grafico.items():
        lista_categorias.append(f"{nome} - R$ {valor:.2f}")
        lista_valores.append(valor)

    # Listas para o Filtro
    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    anos = range(hoje.year - 1, hoje.year + 2)

    context = {
        'receitas': total_receitas,
        'despesas': total_despesas,
        'saldo': saldo,
        'transacoes': transacoes,
        'cotacao_atual': cotacao_dolar,
        'grafico_labels': json.dumps(lista_categorias), 
        'grafico_data': json.dumps(lista_valores),
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'lista_meses': meses,
        'lista_anos': anos,
    }

    return render(request, 'financas/index.html', context)

# --- OUTRAS VIEWS (RESTAURADAS) ---

@login_required
def nova_transacao(request):
    form = TransacaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        transacao = form.save(commit=False)
        transacao.usuario = request.user 
        transacao.save()
        # Adiciona a mensagem de sucesso
        messages.success(request, 'Transação adicionada com sucesso!') 
        return redirect('index')
    return render(request, 'financas/form.html', {'form': form})

@login_required
def editar_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    form = TransacaoForm(request.POST or None, request.FILES or None, instance=transacao)
    if form.is_valid():
        form.save()
        # Adiciona a mensagem de edição
        messages.success(request, 'Transação atualizada com sucesso!')
        return redirect('index')
    return render(request, 'financas/form.html', {'form': form})

@login_required
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    transacao.delete()
    # Adiciona a mensagem de exclusão
    messages.success(request, 'Transação removida!')
    return redirect('index')