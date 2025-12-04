from django import forms
from .models import Transacao

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        # A lista com todos os campos e as vírgulas corretas
        fields = ['descricao', 'valor', 'moeda', 'data', 'categoria', 'observacoes', 'comprovante']
        
        # O widgets fica DENTRO da class Meta (com recuo)
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }