from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import json
import yfinance as yf
from decimal import Decimal # <--- Importante para somar dinheiro
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Transacao, Investimento, MetaCategoria, Categoria, MetaFinanceira
from .forms import TransacaoForm, InvestimentoForm, MetaForm

@login_required
def index(request):
    # 1. Filtros de Data (Isso continua igual, serve para a LISTA na tela)
    mes_atual = int(request.GET.get('mes', datetime.now().month))
    ano_atual = int(request.GET.get('ano', datetime.now().year))

    # Lista filtrada (Só mostra o que é deste mês)
    transacoes_mes = Transacao.objects.filter(
        usuario=request.user,
        data__month=mes_atual,
        data__year=ano_atual
    ).order_by('-data')

    # 2. Cálculos do MÊS (Para mostrar quanto entrou/saiu SÓ em Janeiro)
    receitas_mes = transacoes_mes.filter(categoria__tipo='R').aggregate(Sum('valor'))['valor__sum'] or 0
    despesas_mes = transacoes_mes.filter(categoria__tipo='D').aggregate(Sum('valor'))['valor__sum'] or 0
    
    # --- AQUI ESTÁ A MUDANÇA PRINCIPAL ---
    
    # Para o saldo ser REAL, precisamos somar TUDO desde o início, não só o mês atual.
    # Criamos uma consulta nova sem filtro de data:
    todas_transacoes = Transacao.objects.filter(usuario=request.user)
    
    receita_total_global = todas_transacoes.filter(categoria__tipo='R').aggregate(Sum('valor'))['valor__sum'] or 0
    despesa_total_global = todas_transacoes.filter(categoria__tipo='D').aggregate(Sum('valor'))['valor__sum'] or 0
    
    # Esse é o saldo que vai aparecer no card (Agora ele não zera mais)
    saldo_real = receita_total_global - despesa_total_global
    
    # -------------------------------------

    # 3. Lógica do Salário (Mantive a do mês, mas você pode mudar se quiser)
    total_salario = receitas_mes

    # 4. Lógica das Metas (Continua igual)
    metas = MetaFinanceira.objects.filter(usuario=request.user)
    lista_metas_progresso = []

    for meta in metas:
        acumulado = meta.transacoes.aggregate(Sum('valor'))['valor__sum'] or 0
        if meta.valor_alvo > 0:
            porcentagem = (acumulado / meta.valor_alvo) * 100
        else:
            porcentagem = 0

        lista_metas_progresso.append({
            'nome': meta.nome,
            'alvo': meta.valor_alvo,
            'acumulado': acumulado,
            'porcentagem': min(porcentagem, 100),
            'porcentagem_real': porcentagem,
            'cor': 'success' if porcentagem >= 100 else 'primary'
        })

    # Contexto
    context = {
        'transacoes': transacoes_mes, # Manda só as do mês para a lista
        'receitas': receitas_mes,     # Mostra receita do mês
        'despesas': despesas_mes,     # Mostra despesa do mês
        'saldo': saldo_real,          # <--- Manda o SALDO GLOBAL (Acumulado)
        'total_salario': total_salario,
        'lista_metas_progresso': lista_metas_progresso,
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'lista_meses': [(i, datetime(2000, i, 1).strftime('%B').capitalize()) for i in range(1, 13)],
        'lista_anos': range(2023, 2031),
    }

    return render(request, 'financas/index.html', context)

# --- OUTRAS VIEWS (CRUD) ---

@login_required
def nova_transacao(request):
    # Pega o tipo da URL (ex: ?tipo=receita)
    tipo_url = request.GET.get('tipo') 
    
    if request.method == 'POST':
        form = TransacaoForm(request.POST, request.FILES)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.usuario = request.user
            transacao.save()
            return redirect('index')
    else:
        # Se veio 'receita' na URL, a gente tenta achar uma categoria de Receita para pre-selecionar
        form = TransacaoForm()
        if tipo_url == 'receita':
            # Filtra o campo categoria para mostrar só Receitas (opcional)
            form.fields['categoria'].queryset = Categoria.objects.filter(tipo='R')

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

@login_required
def clonar_despesas_mes_anterior(request):
    # 1. Descobrir qual é o mês/ano passado
    hoje = datetime.now().date()
    if hoje.month == 1:
        mes_anterior = 12
        ano_anterior = hoje.year - 1
    else:
        mes_anterior = hoje.month - 1
        ano_anterior = hoje.year

    # 2. Buscar as despesas desse mês passado
    despesas_antigas = Transacao.objects.filter(
        usuario=request.user,
        categoria__tipo='D', # Só queremos despesas, não receitas
        data__month=mes_anterior,
        data__year=ano_anterior
    )

    if not despesas_antigas.exists():
        messages.error(request, "Não encontrei despesas no mês passado para copiar.")
        return redirect('index')

    # 3. Criar as cópias
    contador = 0
    for despesa in despesas_antigas:
        # Tenta manter o mesmo dia (ex: dia 15). Se der erro (ex: dia 31 em fev), usa dia 28.
        try:
            nova_data = despesa.data.replace(month=hoje.month, year=hoje.year)
        except ValueError:
            nova_data = despesa.data.replace(day=28, month=hoje.month, year=hoje.year)

        Transacao.objects.create(
            descricao=despesa.descricao, # Mantém o mesmo nome
            valor=despesa.valor,
            categoria=despesa.categoria,
            data=nova_data, # Data atualizada para este mês
            usuario=request.user,
            moeda=despesa.moeda,
            observacoes="Cópia automática do mês anterior" # Para você saber o que foi robô
        )
        contador += 1

    messages.success(request, f"{contador} despesas do mês passado foram clonadas para hoje!")
    return redirect('index')

@login_required
def remover_transacao(request, id):
    transacao = get_object_or_404(Transacao, pk=id, usuario=request.user)
    transacao.delete()
    messages.success(request, "Transação removida com sucesso!")
    return redirect('index')

@csrf_exempt # Permite que o Twilio mande dados sem estar logado no site
def bot_whatsapp(request):
    if request.method == 'POST':
        # 1. Pega a mensagem que chegou do WhatsApp
        mensagem = request.POST.get('Body')  # Ex: "Uber 15.90"
        
        # 2. Tenta entender o texto
        try:
            # Separa o texto por espaços
            partes = mensagem.split() 
            
            # A última parte é o valor (Ex: 15.90)
            valor_str = partes[-1].replace(',', '.')
            valor = float(valor_str)
            
            # O resto é a descrição (Ex: Uber)
            descricao = " ".join(partes[:-1])
            
            # 3. Define configurações padrão (MVP)
            # Pega o usuário principal (admin)
            usuario = User.objects.first() 
            # Pega a primeira categoria de Despesa que achar
            categoria = Categoria.objects.filter(tipo='D').first()
            
            # 4. Salva no Banco de Dados
            Transacao.objects.create(
                descricao=descricao,
                valor=valor,
                data=datetime.now().date(),
                categoria=categoria,
                usuario=usuario,
                moeda='BRL'
            )
            
            return HttpResponse("✅ Gasto salvo!")
            
        except Exception as e:
            # Se a pessoa mandou texto errado
            return HttpResponse(f"❌ Erro! Mande assim: 'Uber 20.00'")

    return HttpResponse("Bot rodando!")

@login_required
def criar_meta(request):
    if request.method == 'POST':
        form = MetaForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user
            meta.save()
            messages.success(request, "Nova meta criada com sucesso!")
            return redirect('index')
    else:
        form = MetaForm()
    return render(request, 'financas/form_meta.html', {'form': form})