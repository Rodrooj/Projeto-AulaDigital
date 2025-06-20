from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorialViewSet

router = DefaultRouter()
router.register(r'tutoriais', TutorialViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

