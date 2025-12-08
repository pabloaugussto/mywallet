from django.contrib import admin
from .models import Categoria, Transacao, Investimento

admin.site.register(Categoria)
admin.site.register(Transacao)
admin.site.register(Investimento)