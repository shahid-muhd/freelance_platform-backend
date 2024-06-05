from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers


urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register<str:token>", views.RegisterView.as_view(), name="register_with_params"),
    path("create-account/", views.create_account, name="create_account"),
    path("user/", views.UserView.as_view(), name="user"),
    path("user/<int:user_id>/", views.UserView.as_view(), name="user-specific"),
    path("recover/", views.AccountRecovery.as_view(), name="recover"),
    path("logout/", views.LogoutView.as_view(), name="logout"), 
]
