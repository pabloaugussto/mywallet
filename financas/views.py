import requests
import json
import yfinance as yf
from decimal import Decimal # <--- Importante para somar dinheiro
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transacao, Investimento
from .forms import TransacaoForm, InvestimentoForm

@login_required
def index(request):
    # --- 0. AUTOMAÇÃO PLUXEE (O ROBÔ DO VR) ---
    # Verifica se existe um investimento chamado PLUXEE
    pluxee = Investimento.objects.filter(simbolo__iexact='PLUXEE', usuario=request.user).first()
    
    if pluxee:
        hoje = datetime.now().date()
        ultimo = pluxee.ultimo_deposito
        
        # Se nunca rodou (campo vazio), marca data de ontem para começar a valer hoje
        if not ultimo:
            pluxee.ultimo_deposito = hoje
            pluxee.save()
            ultimo = hoje

        # LÓGICA: Se hoje é um mês diferente do último depósito
        # E hoje é dia 30 ou 31 (Dia do pagamento)
        if hoje > ultimo and hoje.day >= 30 and hoje.month != ultimo.month:
            
            valor_a_cair = 0
            
            # REGRA 1: Dezembro de 2025 (Cai 300)
            if hoje.year == 2025 and hoje.month == 12:
                valor_a_cair = 300.00
            
            # REGRA 2: Janeiro de 2026 em diante (Cai 380)
            elif hoje.year >= 2026:
                valor_a_cair = 380.00
            
            # Se tiver valor para cair, atualiza!
            if valor_a_cair > 0:
                pluxee.quantidade += Decimal(valor_a_cair) # Soma ao saldo existente
                pluxee.ultimo_deposito = hoje # Marca que já pagou este mês
                pluxee.save()
                messages.success(request, f'💰 Pluxee: Pingou R$ {valor_a_cair} na conta!')

    # --- 1. Filtros de Data ---
    hoje_dt = datetime.now()
    try:
        mes_atual = int(request.GET.get('mes', hoje_dt.month))
        ano_atual = int(request.GET.get('ano', hoje_dt.year))
    except ValueError:
        mes_atual = hoje_dt.month
        ano_atual = hoje_dt.year

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
    receitas_brl = float(transacoes_do_mes.filter(categoria__tipo='R', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    receitas_usd = float(transacoes_do_mes.filter(categoria__tipo='R', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    total_receitas = receitas_brl + (receitas_usd * cotacao_dolar)

    despesas_brl = float(transacoes_do_mes.filter(categoria__tipo='D', moeda='BRL').aggregate(Sum('valor'))['valor__sum'] or 0)
    despesas_usd = float(transacoes_do_mes.filter(categoria__tipo='D', moeda='USD').aggregate(Sum('valor'))['valor__sum'] or 0)
    total_despesas = despesas_brl + (despesas_usd * cotacao_dolar)

    saldo = total_receitas - total_despesas
    saldo_usd_original = receitas_usd - despesas_usd

    # --- 4. INVESTIMENTOS (Com separação do Pluxee) ---
    investimentos = Investimento.objects.filter(usuario=request.user)
    total_investido = 0
    lista_investimentos = []
    saldo_pluxee = 0 # Variável para o card vermelho

    if investimentos.exists():
        tickers_str = " ".join([i.simbolo for i in investimentos])
        
        try:
            tickers_data = yf.Tickers(tickers_str)
            
            for inv in investimentos:
                cotacao_atual = 0.0
                
                try:
                    if len(investimentos) == 1:
                        ticker = tickers_data.tickers[inv.simbolo]
                    else:
                        ticker = tickers_data.tickers[inv.simbolo]
                        
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        cotacao_atual = hist['Close'].iloc[-1]
                    else:
                        cotacao_atual = 1.0 # Renda Fixa / Manual
                except Exception:
                    cotacao_atual = 1.0 # Erro na API = Renda Fixa
                
                valor_atual = float(inv.quantidade) * cotacao_atual
                total_investido += valor_atual

                # Se for PLUXEE, guarda o valor separado pro Card Vermelho
                if inv.simbolo.upper() == 'PLUXEE':
                    saldo_pluxee = valor_atual

                lista_investimentos.append({
                    'id_investimento': inv.id,
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

    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    anos = range(hoje_dt.year - 1, hoje_dt.year + 2)

    context = {
        'receitas': total_receitas,
        'despesas': total_despesas,
        'saldo': saldo,
        'saldo_usd': saldo_usd_original,
        'saldo_pluxee': saldo_pluxee, # <--- Card Vermelho usa isso
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

@login_required
def editar_investimento(request, pk):
    investimento = get_object_or_404(Investimento, pk=pk)
    form = InvestimentoForm(request.POST or None, instance=investimento)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Investimento atualizado!')
        return redirect('index')
    
    return render(request, 'financas/form.html', {'form': form})