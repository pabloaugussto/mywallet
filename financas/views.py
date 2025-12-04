from django.shortcuts import render, redirect  # <--- O erro estava aqui
from .models import Transacao
from .forms import TransacaoForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

def index(request):
    # Busca todas as transações do banco
    transacoes = Transacao.objects.all()
    
    # Prepara o pacote de dados para enviar ao HTML
    contexto = {
        'transacoes': transacoes
    }
    
    # Renderiza o arquivo html enviando o contexto
    return render(request, 'financas/index.html', contexto)
@login_required
def index(request):
    transacoes = Transacao.objects.all().order_by('-data') # order_by ordena por data (mais recente primeiro)
    contexto = {'transacoes': transacoes}
    return render(request, 'financas/index.html', contexto)
@login_required
def nova_transacao(request):
    # Se o usuário mandou dados (clicou em salvar)
    if request.method == 'POST':
        form = TransacaoForm(request.POST, request.FILES) # request.FILES é obrigatório para imagens!
        
        if form.is_valid():
            # Aqui está o pulo do gato: commit=False
            transacao = form.save(commit=False) 
            transacao.usuario = request.user # Preenchemos o usuário automaticamente
            transacao.save() # Agora sim salvamos no banco
            return redirect('index') # Volta para a home
            
    # Se o usuário está apenas abrindo a página
    else:
        form = TransacaoForm()

    return render(request, 'financas/form.html', {'form': form})
@login_required
def index(request):
    transacoes = Transacao.objects.all().order_by('-data')
    
    # Cálculos Matemáticos (ORM)
    # 1. Filtra só o que é Receita ('R') e soma a coluna 'valor'
    total_receitas = transacoes.filter(categoria__tipo='R').aggregate(Sum('valor'))['valor__sum'] or 0
    
    # 2. Filtra só o que é Despesa ('D') e soma a coluna 'valor'
    total_despesas = transacoes.filter(categoria__tipo='D').aggregate(Sum('valor'))['valor__sum'] or 0
    
    # 3. Calcula o saldo final
    saldo = total_receitas - total_despesas

    contexto = {
        'transacoes': transacoes,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo': saldo
    }
    
    return render(request, 'financas/index.html', contexto)