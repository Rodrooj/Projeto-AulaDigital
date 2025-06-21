from rest_framework import serializers
from .models import Tutorial
from usuarios.serializers import UsuarioPublicoSerializer


class TutorialSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tutorial
    """
    criador = UsuarioPublicoSerializer(read_only=True)
    
    class Meta:
        model = Tutorial
        fields = ['id', 'titulo', 'descricao', 'link_conteudo', 'tipo', 
                 'criador', 'data_publicacao', 'ativo']
        read_only_fields = ['data_publicacao']
    
    def create(self, validated_data):
        """
        Criar tutorial associando ao usuário logado
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['criador'] = request.user
        return super().create(validated_data)


class TutorialListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de tutoriais
    """
    criador_nome = serializers.CharField(source='criador.nome', read_only=True)
    
    class Meta:
        model = Tutorial
        fields = ['id', 'titulo', 'tipo', 'criador_nome', 'data_publicacao']


class TutorialCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de tutoriais
    """
    class Meta:
        model = Tutorial
        fields = ['titulo', 'descricao', 'link_conteudo', 'tipo', 'ativo']
    
    def validate_link_conteudo(self, value):
        """
        Validar se o link é válido
        """
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("O link deve começar com http:// ou https://")
        return value

