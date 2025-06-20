from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Tutorial
from .serializers import (
    TutorialSerializer, TutorialListSerializer, TutorialCreateSerializer
)


class TutorialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com tutoriais
    """
    queryset = Tutorial.objects.filter(ativo=True)
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação
        """
        if self.action == 'list':
            return TutorialListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TutorialCreateSerializer
        return TutorialSerializer

    def get_permissions(self):
        """
        Define permissões baseadas na ação
        """
        if self.action in ['list', 'retrieve']:
            # Qualquer usuário autenticado pode ver tutoriais
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Apenas administradores podem criar/editar/deletar
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filtrar tutoriais baseado no usuário
        """
        queryset = Tutorial.objects.filter(ativo=True)

        # Filtros opcionais
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset.order_by('-data_publicacao')

    def perform_create(self, serializer):
        """
        Associar o criador ao usuário logado
        """
        serializer.save(criador=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Criar tutorial (apenas para administradores)
        """
        if not (request.user.is_superuser or request.user.tipo_usuario == 'administrador'):
            return Response({
                'message': 'Apenas administradores podem criar tutoriais'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Atualizar tutorial (apenas para administradores)
        """
        if not (request.user.is_superuser or request.user.tipo_usuario == 'administrador'):
            return Response({
                'message': 'Apenas administradores podem editar tutoriais'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Deletar tutorial (soft delete - apenas desativar)
        """
        if not (request.user.is_superuser or request.user.tipo_usuario == 'administrador'):
            return Response({
                'message': 'Apenas administradores podem deletar tutoriais'
            }, status=status.HTTP_403_FORBIDDEN)

        tutorial = self.get_object()
        tutorial.ativo = False
        tutorial.save()

        return Response({
            'message': 'Tutorial desativado com sucesso'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Endpoint para buscar tutoriais por título ou descrição
        """
        query = request.query_params.get('q', '')
        tipo = request.query_params.get('tipo', '')

        queryset = self.get_queryset()

        if query:
            queryset = queryset.filter(
                Q(titulo__icontains=query) |
                Q(descricao__icontains=query)
            )

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        serializer = TutorialListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """
        Endpoint para listar tutoriais agrupados por tipo
        """
        videos = Tutorial.objects.filter(ativo=True, tipo='video').order_by('-data_publicacao')
        textos = Tutorial.objects.filter(ativo=True, tipo='texto').order_by('-data_publicacao')

        return Response({
            'videos': TutorialListSerializer(videos, many=True).data,
            'textos': TutorialListSerializer(textos, many=True).data
        })

    @action(detail=False, methods=['get'])
    def recentes(self, request):
        """
        Endpoint para obter tutoriais mais recentes
        """
        limit = int(request.query_params.get('limit', 5))
        tutoriais = Tutorial.objects.filter(ativo=True).order_by('-data_publicacao')[:limit]

        serializer = TutorialListSerializer(tutoriais, many=True)
        return Response(serializer.data)

