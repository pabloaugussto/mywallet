import requests
import json
import yfinance as yf
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transacao, Investimento
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

    transacoes_do_mes = Transacao.objects.filter(
        data__month=mes_atual, 
        data__year=ano_atual,
        usuario=request.user
    )

    # --- 2. Cotação do Dólar (AwesomeAPI) ---
    cotacao_dolar = 6.00 
    try:
        response = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=2)
        if response.status_code == 200:
            data = response.json()
            cotacao_dolar = float(data['USDBRL']['bid'])
    except:
        pass 

    # --- 3. Totais (Receita vs Despesa) ---
    # Receitas
    receitas_brl = float(transacoes_do_mes.filter(categoria__tipo='R', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    receitas_usd = float(transacoes_do_mes.filter(categoria__tipo='R', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    total_receitas = receitas_brl + (receitas_usd * cotacao_dolar)

    # Despesas
    despesas_brl = float(transacoes_do_mes.filter(categoria__tipo='D', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    despesas_usd = float(transacoes_do_mes.filter(categoria__tipo='D', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    total_despesas = despesas_brl + (despesas_usd * cotacao_dolar)

    # Saldos
    saldo = total_receitas - total_despesas
    saldo_usd_original = receitas_usd - despesas_usd

    # --- 4. INVESTIMENTOS (Com lógica para Renda Fixa) ---
    investimentos = Investimento.objects.filter(usuario=request.user)
    total_investido = 0
    lista_investimentos = []

    if investimentos.exists():
        # Junta todos os símbolos numa string só para buscar rápido no Yahoo
        tickers_str = " ".join([i.simbolo for i in investimentos])
        
        try:
            tickers_data = yf.Tickers(tickers_str)
            
            for inv in investimentos:
                cotacao_atual = 0.0
                
                # Tenta buscar cotação no Yahoo Finance
                try:
                    # Se tiver um único ativo, a estrutura do yfinance muda um pouco,
                    # então acessamos direto pelo símbolo se possível
                    if len(investimentos) == 1:
                        ticker = tickers_data.tickers[inv.simbolo]
                    else:
                        ticker = tickers_data.tickers[inv.simbolo]
                        
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        cotacao_atual = hist['Close'].iloc[-1]
                    else:
                        # TRUQUE DO COFRINHO: Se não tem histórico (ex: MERCADO_PAGO),
                        # assume preço = 1.0 (Renda Fixa / Dinheiro)
                        cotacao_atual = 1.0
                except Exception:
                    # Se der qualquer erro na busca desse ativo específico,
                    # assume 1.0 para não quebrar a tela
                    cotacao_atual = 1.0
                
                valor_atual = float(inv.quantidade) * cotacao_atual
                total_investido += valor_atual
                
                lista_investimentos.append({
                    'simbolo': inv.simbolo,
                    'qtd': inv.quantidade,
                    'preco': cotacao_atual,
                    'total': valor_atual
                })
        except Exception as e:
            print(f"Erro Geral no YFinance: {e}")

    # --- 5. Gráfico e Tabela ---
    transacoes = transacoes_do_mes.order_by('-data')
    
    dados_grafico = {} 
    
    # LÓGICA DO GRÁFICO (Convertendo Dólar e Filtrando Despesa)
    for t in transacoes_do_mes:
        if t.categoria.tipo == 'D':
            valor_real = float(t.valor)
            if t.moeda == 'USD':
                valor_real = valor_real * cotacao_dolar
            
            nome = t.categoria.nome
            dados_grafico[nome] = dados_grafico.get(nome, 0) + valor_real

    lista_categorias = []
    lista_valores = []
    
    for nome, valor in dados_grafico.items():
        lista_categorias.append(f"{nome} - R$ {valor:.2f}")
        lista_valores.append(valor)

    # Listas auxiliares para o filtro
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
        'saldo_usd': saldo_usd_original,
        'total_investido': total_investido,
        'lista_investimentos': lista_investimentos,
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

# --- OUTRAS VIEWS (CRUD) ---

@login_required
def nova_transacao(request):
    form = TransacaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        transacao = form.save(commit=False)
        transacao.usuario = request.user 
        transacao.save()
        messages.success(request, 'Transação adicionada com sucesso!')
        return redirect('index')
    return render(request, 'financas/form.html', {'form': form})

@login_required
def editar_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    form = TransacaoForm(request.POST or None, request.FILES or None, instance=transacao)
    if form.is_valid():
        form.save()
        messages.success(request, 'Transação atualizada com sucesso!')
        return redirect('index')
    return render(request, 'financas/form.html', {'form': form})

@login_required
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk)
    transacao.delete()
    messages.success(request, 'Transação removida!')
    return redirect('index')