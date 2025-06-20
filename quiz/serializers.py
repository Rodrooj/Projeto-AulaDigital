from rest_framework import serializers
from .models import Pergunta, Alternativa, ResultadoQuiz
from usuarios.serializers import UsuarioPublicoSerializer


class AlternativaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Alternativa
    """

    class Meta:
        model = Alternativa
        fields = ['id', 'texto_alternativa', 'correta']


class AlternativaPublicaSerializer(serializers.ModelSerializer):
    """
    Serializer público para alternativas (sem mostrar qual é a correta)
    """

    class Meta:
        model = Alternativa
        fields = ['id', 'texto_alternativa']


class PerguntaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para o modelo Pergunta (para administradores)
    """
    alternativas = AlternativaSerializer(many=True, read_only=True)
    criador = UsuarioPublicoSerializer(read_only=True)

    class Meta:
        model = Pergunta
        fields = ['id', 'enunciado', 'dificuldade', 'criador', 'data_criacao',
                  'ativa', 'alternativas']
        read_only_fields = ['data_criacao']


class PerguntaPublicaSerializer(serializers.ModelSerializer):
    """
    Serializer público para perguntas (para alunos jogarem)
    """
    alternativas = AlternativaPublicaSerializer(many=True, read_only=True)

    class Meta:
        model = Pergunta
        fields = ['id', 'enunciado', 'dificuldade', 'alternativas']


class PerguntaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de perguntas com alternativas
    """
    alternativas = AlternativaSerializer(many=True)

    class Meta:
        model = Pergunta
        fields = ['enunciado', 'dificuldade', 'ativa', 'alternativas']

    def validate_alternativas(self, value):
        """
        Validar que há exatamente 4 alternativas e apenas 1 correta
        """
        if len(value) != 4:
            raise serializers.ValidationError("Deve haver exatamente 4 alternativas.")

        corretas = sum(1 for alt in value if alt.get('correta', False))
        if corretas != 1:
            raise serializers.ValidationError("Deve haver exatamente 1 alternativa correta.")

        return value

    def create(self, validated_data):
        """
        Criar pergunta com suas alternativas
        """
        alternativas_data = validated_data.pop('alternativas')
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            validated_data['criador'] = request.user

        pergunta = Pergunta.objects.create(**validated_data)

        for alternativa_data in alternativas_data:
            Alternativa.objects.create(pergunta=pergunta, **alternativa_data)

        return pergunta


class ResultadoQuizSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo ResultadoQuiz
    """
    aluno = UsuarioPublicoSerializer(read_only=True)
    pergunta = PerguntaPublicaSerializer(read_only=True)
    alternativa_selecionada = AlternativaSerializer(read_only=True)

    class Meta:
        model = ResultadoQuiz
        fields = ['id', 'aluno', 'pergunta', 'alternativa_selecionada',
                  'acertou', 'data_tentativa']
        read_only_fields = ['acertou', 'data_tentativa']


class ResponderPerguntaSerializer(serializers.Serializer):
    """
    Serializer para responder uma pergunta do quiz
    """
    pergunta_id = serializers.IntegerField()
    alternativa_id = serializers.IntegerField()

    def validate(self, data):
        """
        Validar se a pergunta e alternativa existem e estão relacionadas
        """
        try:
            pergunta = Pergunta.objects.get(id=data['pergunta_id'], ativa=True)
        except Pergunta.DoesNotExist:
            raise serializers.ValidationError("Pergunta não encontrada ou inativa.")

        try:
            alternativa = Alternativa.objects.get(
                id=data['alternativa_id'],
                pergunta=pergunta
            )
        except Alternativa.DoesNotExist:
            raise serializers.ValidationError("Alternativa não encontrada para esta pergunta.")

        data['pergunta'] = pergunta
        data['alternativa'] = alternativa
        return data


class EstatisticasQuizSerializer(serializers.Serializer):
    """
    Serializer para estatísticas do quiz
    """
    total_perguntas = serializers.IntegerField()
    total_respostas = serializers.IntegerField()
    acertos = serializers.IntegerField()
    erros = serializers.IntegerField()
    percentual_acerto = serializers.FloatField()
    perguntas_por_dificuldade = serializers.DictField()
    acertos_por_dificuldade = serializers.DictField()

