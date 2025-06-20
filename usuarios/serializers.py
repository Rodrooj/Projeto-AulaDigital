from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Usuario
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nome', 'tipo_usuario', 'matricula',
                  'password', 'is_active', 'data_criacao']
        extra_kwargs = {
            'password': {'write_only': True},
            'data_criacao': {'read_only': True},
        }

    def create(self, validated_data):
        """
        Criar novo usuário com senha criptografada
        """
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Atualizar usuário, tratando senha separadamente
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """
    Serializer público para o modelo Usuario (sem informações sensíveis)
    """

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'tipo_usuario', 'data_criacao']


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuário
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('Conta de usuário desativada.')
            else:
                raise serializers.ValidationError('Credenciais inválidas.')
        else:
            raise serializers.ValidationError('Username e password são obrigatórios.')

        return data


class RegistroSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários
    """
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nome', 'tipo_usuario', 'matricula',
                  'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

