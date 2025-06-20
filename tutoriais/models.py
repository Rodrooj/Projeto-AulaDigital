from django.db import models
from django.conf import settings


class Tutorial(models.Model):
    """
    Modelo para armazenar os conteúdos educacionais do AulaDigital
    """
    TIPO_CHOICES = [
        ('video', 'Vídeo'),
        ('texto', 'Texto'),
    ]

    titulo = models.CharField(max_length=255, verbose_name="Título")
    descricao = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do tutorial"
    )
    link_conteudo = models.URLField(
        verbose_name="Link do conteúdo",
        help_text="URL para o vídeo ou artigo do tutorial"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo",
        help_text="Diferencia se o tutorial é em vídeo ou texto"
    )
    criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criador",
        related_name="tutoriais_criados"
    )
    data_publicacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de publicação"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Tutorial"
        verbose_name_plural = "Tutoriais"
        ordering = ['-data_publicacao']
        db_table = 'tutoriais_tutorial'

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"

