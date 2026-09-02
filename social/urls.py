from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    PostViewSet,
    ProfileViewSet,
    RegisterView,
    explore,
    profile_page,
    settings_page,
    social_home,
)

router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profile')
router.register('posts', PostViewSet, basename='post')

urlpatterns = [
    path('', social_home, name='social-home'),
    path('explore/', explore, name='explore'),
    path('settings/', settings_page, name='settings'),
    path('profile/<str:username>/', profile_page, name='profile-page'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]