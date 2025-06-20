from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuração do admin para o modelo Usuario customizado
    """
    list_display = ('username', 'nome', 'email', 'tipo_usuario', 'matricula', 'is_active', 'data_criacao')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff', 'data_criacao')
    search_fields = ('username', 'nome', 'email', 'matricula')
    ordering = ('-data_criacao',)

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome', 'tipo_usuario', 'matricula', 'data_criacao')
        }),
    )

    readonly_fields = ('data_criacao',)

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome', 'tipo_usuario', 'matricula')
        }),
    )

