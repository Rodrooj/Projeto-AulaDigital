from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerguntaViewSet, ResultadoQuizViewSet

router = DefaultRouter()
router.register(r'perguntas', PerguntaViewSet)
router.register(r'resultados', ResultadoQuizViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

