"""
URL configuration for authentication endpoints.
Includes registration, login, and email check routes.
"""
from django.urls import path
from . import views

urlpatterns = [
  path('registration/', views.RegisterView.as_view(), name='register'),
  path('login/', views.LoginView.as_view(), name='login'),
  path('email-check/', views.EmailCheckView.as_view(), name='email-check'),
]