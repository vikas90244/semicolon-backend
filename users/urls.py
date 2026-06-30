from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('guest-login/', views.guest_login, name='guest_login'),
    path('refresh/', views.refresh_token, name='refresh'),
    path('user/', views.get_user, name='user'),
    path('logout/', views.logout, name='logout'),
]
