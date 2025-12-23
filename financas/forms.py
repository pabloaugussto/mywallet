from django import forms
from .models import Transacao, Investimento, MetaFinanceira

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'valor', 'categoria', 'data', 'observacoes', 'comprovante', 'meta_relacionada']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comprovante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'meta_relacionada': forms.Select(attrs={'class': 'form-select'}),
        }

class InvestimentoForm(forms.ModelForm):
    class Meta:
        model = Investimento
        fields = ['simbolo', 'quantidade', 'ultimo_deposito']
        widgets = {
            'simbolo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PETR4.SA'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'ultimo_deposito': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class MetaForm(forms.ModelForm):
    class Meta:
        model = MetaFinanceira
        fields = ['nome', 'valor_alvo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Viagem Disney'}),
            'valor_alvo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }