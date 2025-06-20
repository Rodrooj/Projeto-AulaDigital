from django.contrib import admin
from .models import Pergunta, Alternativa, ResultadoQuiz


class AlternativaInline(admin.TabularInline):
    """
    Inline para editar alternativas dentro da pergunta
    """
    model = Alternativa
    extra = 4
    max_num = 4


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Pergunta
    """
    list_display = ('enunciado_resumido', 'dificuldade', 'criador', 'ativa', 'data_criacao')
    list_filter = ('dificuldade', 'ativa', 'data_criacao')
    search_fields = ('enunciado',)
    ordering = ('-data_criacao',)
    readonly_fields = ('data_criacao',)
    inlines = [AlternativaInline]

    def enunciado_resumido(self, obj):
        return obj.enunciado[:50] + "..." if len(obj.enunciado) > 50 else obj.enunciado

    enunciado_resumido.short_description = "Enunciado"

    fieldsets = (
        ('Pergunta', {
            'fields': ('enunciado', 'dificuldade', 'ativa')
        }),
        ('Metadados', {
            'fields': ('criador', 'data_criacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Alternativa
    """
    list_display = ('texto_resumido', 'pergunta_resumida', 'correta')
    list_filter = ('correta',)
    search_fields = ('texto_alternativa', 'pergunta__enunciado')

    def texto_resumido(self, obj):
        return obj.texto_alternativa[:30] + "..." if len(obj.texto_alternativa) > 30 else obj.texto_alternativa

    texto_resumido.short_description = "Texto"

    def pergunta_resumida(self, obj):
        return obj.pergunta.enunciado[:30] + "..." if len(obj.pergunta.enunciado) > 30 else obj.pergunta.enunciado

    pergunta_resumida.short_description = "Pergunta"


@admin.register(ResultadoQuiz)
class ResultadoQuizAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo ResultadoQuiz
    """
    list_display = ('aluno', 'pergunta_resumida', 'acertou', 'data_tentativa')
    list_filter = ('acertou', 'data_tentativa')
    search_fields = ('aluno__nome', 'pergunta__enunciado')
    ordering = ('-data_tentativa',)
    readonly_fields = ('data_tentativa', 'acertou')

    def pergunta_resumida(self, obj):
        return obj.pergunta.enunciado[:30] + "..." if len(obj.pergunta.enunciado) > 30 else obj.pergunta.enunciado

    pergunta_resumida.short_description = "Pergunta"

