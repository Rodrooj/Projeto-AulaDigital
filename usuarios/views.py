from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.db.models import Q
from .models import Usuario
from .serializers import (
    UsuarioSerializer, UsuarioPublicoSerializer,
    LoginSerializer, RegistroSerializer
)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com usuários
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação
        """
        if self.action == 'list':
            return UsuarioPublicoSerializer
        elif self.action == 'registro':
            return RegistroSerializer
        elif self.action == 'login':
            return LoginSerializer
        return UsuarioSerializer

    def get_permissions(self):
        """
        Define permissões baseadas na ação
        """
        if self.action in ['registro', 'login']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filtrar usuários baseado no tipo de usuário logado
        """
        user = self.request.user
        if user.is_superuser or user.tipo_usuario == 'administrador':
            return Usuario.objects.all()
        else:
            # Usuários normais só veem informações públicas
            return Usuario.objects.filter(is_active=True)

    @action(detail=False, methods=['post'])
    def registro(self, request):
        """
        Endpoint para registro de novos usuários
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Usuário criado com sucesso',
                'user': UsuarioPublicoSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Endpoint para login de usuários
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)

            # Criar ou obter token para API
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'Login realizado com sucesso',
                'user': UsuarioPublicoSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Endpoint para logout de usuários
        """
        if request.user.is_authenticated:
            # Deletar token se existir
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass

            logout(request)
            return Response({
                'message': 'Logout realizado com sucesso'
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Usuário não estava logado'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """
        Endpoint para obter perfil do usuário logado
        """
        if request.user.is_authenticated:
            serializer = UsuarioSerializer(request.user)
            return Response(serializer.data)
        return Response({
            'message': 'Usuário não autenticado'
        }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['put', 'patch'])
    def atualizar_perfil(self, request):
        """
        Endpoint para atualizar perfil do usuário logado
        """
        if request.user.is_authenticated:
            serializer = UsuarioSerializer(
                request.user,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Perfil atualizado com sucesso',
                    'user': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Usuário não autenticado'
        }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Endpoint para buscar usuários por nome ou email
        """
        query = request.query_params.get('q', '')
        tipo = request.query_params.get('tipo', '')

        queryset = self.get_queryset()

        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) |
                Q(email__icontains=query) |
                Q(username__icontains=query)
            )

        if tipo:
            queryset = queryset.filter(tipo_usuario=tipo)

        serializer = UsuarioPublicoSerializer(queryset, many=True)
        return Response(serializer.data)

