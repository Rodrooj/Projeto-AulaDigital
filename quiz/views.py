from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
import random
from .models import Pergunta, Alternativa, ResultadoQuiz
from .serializers import (
    PerguntaSerializer, PerguntaPublicaSerializer, PerguntaCreateSerializer,
    AlternativaSerializer, ResultadoQuizSerializer, ResponderPerguntaSerializer,
    EstatisticasQuizSerializer
)


class PerguntaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com perguntas
    """
    queryset = Pergunta.objects.filter(ativa=True)
    serializer_class = PerguntaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação
        """
        if self.action in ['list', 'retrieve'] and not self.request.user.is_superuser:
            if self.request.user.tipo_usuario != 'administrador':
                return PerguntaPublicaSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PerguntaCreateSerializer
        return PerguntaSerializer

    def get_permissions(self):
        """
        Define permissões baseadas na ação
        """
        if self.action in ['list', 'retrieve', 'aleatoria', 'responder']:
            # Qualquer usuário autenticado pode ver perguntas e responder
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Apenas administradores podem criar/editar/deletar
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filtrar perguntas baseado no usuário e parâmetros
        """
        queryset = Pergunta.objects.filter(ativa=True)

        # Filtros opcionais
        dificuldade = self.request.query_params.get('dificuldade', None)
        if dificuldade:
            queryset = queryset.filter(dificuldade=dificuldade)

        return queryset.order_by('-data_criacao')

    def perform_create(self, serializer):
        """
        Associar o criador ao usuário logado
        """
        serializer.save(criador=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Criar pergunta (apenas para administradores)
        """
        if not (request.user.is_superuser or request.user.tipo_usuario == 'administrador'):
            return Response({
                'message': 'Apenas administradores podem criar perguntas'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Atualizar pergunta (apenas para administradores)
        """
        if not (request.user.is_superuser or request.user.tipo_usuario == 'administrador'):
            return Response({
                'message': 'Apenas administradores podem editar perguntas'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Deletar pergunta (soft delete - apenas desativar)
        """
        if not (request.user.is_superuser or request.user.tipo_usuario == 'administrador'):
            return Response({
                'message': 'Apenas administradores podem deletar perguntas'
            }, status=status.HTTP_403_FORBIDDEN)

        pergunta = self.get_object()
        pergunta.ativa = False
        pergunta.save()

        return Response({
            'message': 'Pergunta desativada com sucesso'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def aleatoria(self, request):
        """
        Endpoint para obter uma pergunta aleatória
        """
        dificuldade = request.query_params.get('dificuldade', None)

        queryset = self.get_queryset()
        if dificuldade:
            queryset = queryset.filter(dificuldade=dificuldade)

        # Obter pergunta aleatória
        count = queryset.count()
        if count == 0:
            return Response({
                'message': 'Nenhuma pergunta encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        random_index = random.randint(0, count - 1)
        pergunta = queryset[random_index]

        serializer = PerguntaPublicaSerializer(pergunta)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def responder(self, request):
        """
        Endpoint para responder uma pergunta
        """
        serializer = ResponderPerguntaSerializer(data=request.data)
        if serializer.is_valid():
            pergunta = serializer.validated_data['pergunta']
            alternativa = serializer.validated_data['alternativa']

            # Verificar se o usuário é aluno
            if request.user.tipo_usuario != 'aluno':
                return Response({
                    'message': 'Apenas alunos podem responder perguntas'
                }, status=status.HTTP_403_FORBIDDEN)

            # Criar resultado
            resultado = ResultadoQuiz.objects.create(
                aluno=request.user,
                pergunta=pergunta,
                alternativa_selecionada=alternativa
            )

            # Obter a alternativa correta
            alternativa_correta = pergunta.get_alternativa_correta()

            return Response({
                'acertou': resultado.acertou,
                'alternativa_correta': AlternativaSerializer(alternativa_correta).data,
                'explicacao': f"A resposta correta é: {alternativa_correta.texto_alternativa}"
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def por_dificuldade(self, request):
        """
        Endpoint para listar perguntas agrupadas por dificuldade
        """
        faceis = self.get_queryset().filter(dificuldade='facil')
        medias = self.get_queryset().filter(dificuldade='medio')
        dificeis = self.get_queryset().filter(dificuldade='dificil')

        serializer_class = self.get_serializer_class()

        return Response({
            'facil': serializer_class(faceis, many=True).data,
            'medio': serializer_class(medias, many=True).data,
            'dificil': serializer_class(dificeis, many=True).data
        })


class ResultadoQuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar resultados do quiz
    """
    queryset = ResultadoQuiz.objects.all()
    serializer_class = ResultadoQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar resultados baseado no usuário
        """
        user = self.request.user

        if user.is_superuser or user.tipo_usuario == 'administrador':
            # Administradores veem todos os resultados
            return ResultadoQuiz.objects.all().order_by('-data_tentativa')
        elif user.tipo_usuario == 'aluno':
            # Alunos veem apenas seus próprios resultados
            return ResultadoQuiz.objects.filter(aluno=user).order_by('-data_tentativa')
        else:
            # Professores não têm acesso aos resultados por padrão
            return ResultadoQuiz.objects.none()

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        Endpoint para obter estatísticas do quiz
        """
        user = request.user

        if user.tipo_usuario == 'aluno':
            # Estatísticas do próprio aluno
            resultados = ResultadoQuiz.objects.filter(aluno=user)
        elif user.is_superuser or user.tipo_usuario == 'administrador':
            # Estatísticas gerais para administradores
            resultados = ResultadoQuiz.objects.all()
        else:
            return Response({
                'message': 'Acesso negado'
            }, status=status.HTTP_403_FORBIDDEN)

        total_respostas = resultados.count()
        acertos = resultados.filter(acertou=True).count()
        erros = total_respostas - acertos
        percentual_acerto = (acertos / total_respostas * 100) if total_respostas > 0 else 0

        # Estatísticas por dificuldade
        perguntas_por_dificuldade = {}
        acertos_por_dificuldade = {}

        for dificuldade in ['facil', 'medio', 'dificil']:
            resultados_dif = resultados.filter(pergunta__dificuldade=dificuldade)
            total_dif = resultados_dif.count()
            acertos_dif = resultados_dif.filter(acertou=True).count()

            perguntas_por_dificuldade[dificuldade] = total_dif
            acertos_por_dificuldade[dificuldade] = acertos_dif

        total_perguntas = Pergunta.objects.filter(ativa=True).count()

        dados = {
            'total_perguntas': total_perguntas,
            'total_respostas': total_respostas,
            'acertos': acertos,
            'erros': erros,
            'percentual_acerto': round(percentual_acerto, 2),
            'perguntas_por_dificuldade': perguntas_por_dificuldade,
            'acertos_por_dificuldade': acertos_por_dificuldade
        }

        serializer = EstatisticasQuizSerializer(dados)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def historico(self, request):
        """
        Endpoint para obter histórico de respostas do usuário
        """
        if request.user.tipo_usuario != 'aluno':
            return Response({
                'message': 'Apenas alunos podem ver o histórico'
            }, status=status.HTTP_403_FORBIDDEN)

        resultados = self.get_queryset()[:20]  # Últimas 20 respostas
        serializer = self.get_serializer(resultados, many=True)
        return Response(serializer.data)

