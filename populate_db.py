"""
Script para popular o banco de dados com dados iniciais
baseado no script SQL fornecido
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auladigital_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from tutoriais.models import Tutorial
from quiz.models import Pergunta, Alternativa

User = get_user_model()

def criar_dados_iniciais():
    print("Criando dados iniciais...")

    # Criar usuários
    if not User.objects.filter(username="prof_carlos").exists():
        professor = User.objects.create_user(
            username="prof_carlos",
            email="carlos@email.com",
            password="senha_segura_123",
            nome="Prof. Carlos",
            tipo_usuario="professor",
            matricula="P98765"
        )
        print(f"Professor criado: {professor.nome}")

    if not User.objects.filter(username="ana_julia").exists():
        aluno = User.objects.create_user(
            username="ana_julia",
            email="ana.j@email.com",
            password="senha_segura_123", # Senha corrigida
            nome="Ana Julia",
            tipo_usuario="aluno",
            matricula="A12345"
        )
        print(f"Aluno criado: {aluno.nome}")

    # Obter administrador
    admin = User.objects.get(username="admin")

    # Limpar tutoriais existentes para evitar duplicatas
    Tutorial.objects.all().delete()
    print("Tutoriais existentes limpos.")

    # Criar tutoriais com os links fornecidos
    tutoriais_data = [
        {
            "titulo": "Como Usar o Google Docs",
            "descricao": "Aprenda o básico do Google Docs para criar e compartilhar documentos.",
            "link_conteudo": "https://www.youtube.com/watch?v=qumPQRAhnQM",
            "tipo": "video"
        },
        {
            "titulo": "Como criar Slides eficazes",
            "descricao": "Aprenda técnicas para criar apresentações impactantes e envolventes.",
            "link_conteudo": "https://www.youtube.com/watch?v=ZwJUVybOWxw",
            "tipo": "video"
        },
        {
            "titulo": "Como fazer Pesquisas na Internet",
            "descricao": "Guia completo para pesquisas eficientes e confiáveis online.",
            "link_conteudo": "https://juntosnacasa.casadaciencia.ufrj.br/2020/09/02/5-dicas-para-fazer-pesquisas-na-internet/",
            "tipo": "texto"
        },
        {
            "titulo": "Como usar IA em sala de aula",
            "descricao": "Descubra como integrar ferramentas de IA no ensino.",
            "link_conteudo": "https://www.youtube.com/watch?v=7CaXE1vhWCE",
            "tipo": "video"
        },
        {
            "titulo": "Como usar projetores",
            "descricao": "Manual prático para configurar e usar projetores em sala de aula.",
            "link_conteudo": "https://www.uol.com.br/tilt/reportagens-especiais/como-funciona-um-projetor/",
            "tipo": "texto"
        }
    ]

    for tutorial_data in tutoriais_data:
        if not Tutorial.objects.filter(titulo=tutorial_data["titulo"]).exists():
            Tutorial.objects.create(
                titulo=tutorial_data["titulo"],
                descricao=tutorial_data["descricao"],
                link_conteudo=tutorial_data["link_conteudo"],
                tipo=tutorial_data["tipo"],
                criador=admin
            )
            #print(f"Tutorial criado: {tutorial_data["titulo"]}")

    # Limpar perguntas e alternativas existentes para evitar duplicatas
    Pergunta.objects.all().delete()
    print("Perguntas existentes limpas.")

    # Criar perguntas
    perguntas_data = [
        {
            "enunciado": "Qual ferramenta é usada para criar apresentações de slides?",
            "dificuldade": "facil",
            "alternativas": [
                ("Google Docs", False),
                ("Google Sheets", False),
                ("Google Slides", True),
                ("Google Forms", False),
            ]
        },
        {
            "enunciado": "Qual é a principal vantagem do Google Docs em relação ao Microsoft Word tradicional?",
            "dificuldade": "medio",
            "alternativas": [
                ("Permite colaboração em tempo real", True),
                ("Tem mais recursos de formatação", False),
                ("É mais rápido para abrir", False),
                ("Ocupa menos espaço no computador", False),
            ]
        },
        {
            "enunciado": "Para que serve o Google Forms?",
            "dificuldade": "facil",
            "alternativas": [
                ("Criar planilhas", False),
                ("Fazer apresentações", False),
                ("Criar formulários e questionários", True),
                ("Editar imagens", False),
            ]
        },
        {
            "enunciado": "Qual ferramenta de IA pode ajudar professores a criar conteúdo educacional?",
            "dificuldade": "dificil",
            "alternativas": [
                ("ChatGPT", True),
                ("Photoshop", False),
                ("Excel", False),
                ("PowerPoint", False),
            ]
        }
    ]

    for pergunta_data in perguntas_data:
        if not Pergunta.objects.filter(enunciado=pergunta_data["enunciado"]).exists():
            pergunta = Pergunta.objects.create(
                enunciado=pergunta_data["enunciado"],
                dificuldade=pergunta_data["dificuldade"],
                criador=admin
            )

            for texto, correta in pergunta_data["alternativas"]:
                Alternativa.objects.create(
                    pergunta=pergunta,
                    texto_alternativa=texto,
                    correta=correta
                )

            #print(f"Pergunta criada: {pergunta_data["enunciado"][:50]}...")

    print("Dados iniciais criados com sucesso!")

if __name__ == "__main__":
    criar_dados_iniciais()



