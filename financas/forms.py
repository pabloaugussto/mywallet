from django import forms
from .models import Transacao, Investimento

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        # A lista com todos os campos e as vírgulas corretas
        fields = ['descricao', 'valor', 'moeda', 'data', 'categoria', 'observacoes', 'comprovante']
        
        # O widgets fica DENTRO da class Meta (com recuo)
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class InvestimentoForm(forms.ModelForm):
    class Meta:
        model = Investimento
        fields = ['simbolo', 'quantidade']
        widgets = {
            'simbolo': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
        }