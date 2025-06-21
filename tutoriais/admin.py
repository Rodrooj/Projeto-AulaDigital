from django.contrib import admin
from .models import Tutorial


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Tutorial
    """
    list_display = ('titulo', 'tipo', 'criador', 'ativo', 'data_publicacao')
    list_filter = ('tipo', 'ativo', 'data_publicacao')
    search_fields = ('titulo', 'descricao')
    ordering = ('-data_publicacao',)
    readonly_fields = ('data_publicacao',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'tipo', 'link_conteudo')
        }),
        ('Configurações', {
            'fields': ('criador', 'ativo')
        }),
        ('Metadados', {
            'fields': ('data_publicacao',),
            'classes': ('collapse',)
        }),
    )

