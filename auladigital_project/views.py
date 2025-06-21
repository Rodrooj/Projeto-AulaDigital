from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


def home(request):
    """Página inicial"""
    return render(request, 'home.html')


def tutoriais_view(request):
    """Página de tutoriais"""
    return render(request, 'tutoriais.html')


def quiz_view(request):
    """Página do quiz"""
    return render(request, 'quiz.html')


def login_view(request):
    """Página de login"""
    return render(request, 'auth/login.html')


def registro_view(request):
    """Página de registro"""
    return render(request, 'auth/registro.html')


def perfil_view(request):
    """Página de perfil do usuário"""
    return render(request, 'auth/perfil.html')

