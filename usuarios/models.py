from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Modelo customizado de usuário que estende o AbstractUser do Django
    para incluir campos específicos do AulaDigital
    """
    TIPO_USUARIO_CHOICES = [
        ('professor', 'Professor'),
        ('aluno', 'Aluno'),
        ('administrador', 'Administrador'),
    ]
    
    nome = models.CharField(max_length=255, verbose_name="Nome completo")
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES,
        verbose_name="Tipo de usuário",
        help_text="Define o papel do usuário no sistema"
    )
    matricula = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="Matrícula",
        help_text="Matrícula para professores ou alunos"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = 'usuarios_usuario'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_usuario_display()})"
    
    @property
    def is_professor(self):
        return self.tipo_usuario == 'professor'
    
    @property
    def is_aluno(self):
        return self.tipo_usuario == 'aluno'
    
    @property
    def is_administrador(self):
        return self.tipo_usuario == 'administrador'

