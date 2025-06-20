from django.db import models
from django.conf import settings


class Pergunta(models.Model):
    """
    Modelo para armazenar as perguntas do EducaQuiz
    """
    DIFICULDADE_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Médio'),
        ('dificil', 'Difícil'),
    ]

    enunciado = models.TextField(
        verbose_name="Enunciado",
        help_text="O texto da pergunta do quiz"
    )
    dificuldade = models.CharField(
        max_length=10,
        choices=DIFICULDADE_CHOICES,
        verbose_name="Dificuldade"
    )
    criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criador",
        related_name="perguntas_criadas"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação"
    )
    ativa = models.BooleanField(default=True, verbose_name="Ativa")

    class Meta:
        verbose_name = "Pergunta"
        verbose_name_plural = "Perguntas"
        ordering = ['-data_criacao']
        db_table = 'quiz_pergunta'

    def __str__(self):
        return f"{self.enunciado[:50]}... ({self.get_dificuldade_display()})"

    def get_alternativas(self):
        """Retorna todas as alternativas desta pergunta"""
        return self.alternativas.all()

    def get_alternativa_correta(self):
        """Retorna a alternativa correta desta pergunta"""
        return self.alternativas.filter(correta=True).first()


class Alternativa(models.Model):
    """
    Modelo para armazenar as opções de resposta para cada pergunta
    """
    pergunta = models.ForeignKey(
        Pergunta,
        on_delete=models.CASCADE,
        related_name="alternativas",
        verbose_name="Pergunta"
    )
    texto_alternativa = models.TextField(verbose_name="Texto da alternativa")
    correta = models.BooleanField(
        default=False,
        verbose_name="Correta",
        help_text="TRUE se esta for a resposta correta, FALSE caso contrário"
    )

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"
        db_table = 'quiz_alternativa'
        # Garante que apenas uma alternativa por pergunta seja marcada como correta
        constraints = [
            models.UniqueConstraint(
                fields=['pergunta'],
                condition=models.Q(correta=True),
                name='unique_correct_answer_per_question'
            )
        ]

    def __str__(self):
        status = "✓" if self.correta else "✗"
        return f"{status} {self.texto_alternativa[:30]}..."


class ResultadoQuiz(models.Model):
    """
    Modelo para registrar o desempenho e as tentativas dos alunos no quiz
    """
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Aluno",
        related_name="resultados_quiz"
    )
    pergunta = models.ForeignKey(
        Pergunta,
        on_delete=models.CASCADE,
        verbose_name="Pergunta"
    )
    alternativa_selecionada = models.ForeignKey(
        Alternativa,
        on_delete=models.CASCADE,
        verbose_name="Alternativa selecionada"
    )
    acertou = models.BooleanField(verbose_name="Acertou")
    data_tentativa = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da tentativa"
    )

    class Meta:
        verbose_name = "Resultado do Quiz"
        verbose_name_plural = "Resultados do Quiz"
        ordering = ['-data_tentativa']
        db_table = 'quiz_resultadoquiz'

    def __str__(self):
        status = "✓" if self.acertou else "✗"
        return f"{self.aluno.nome} - {status} - {self.pergunta.enunciado[:30]}..."

    def save(self, *args, **kwargs):
        """
        Override do save para automaticamente definir se o aluno acertou
        baseado na alternativa selecionada
        """
        self.acertou = self.alternativa_selecionada.correta
        super().save(*args, **kwargs)

