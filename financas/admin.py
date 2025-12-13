from django.contrib import admin
from .models import Categoria, Transacao, Investimento, MetaCategoria

admin.site.register(Categoria)
admin.site.register(Transacao)
admin.site.register(Investimento)
admin.site.register(MetaCategoria)