from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, PostViewSet, ProfileViewSet, RegisterView

router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profile')
router.register('posts', PostViewSet, basename='post')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]