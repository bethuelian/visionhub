# urls.py (app-level)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('join/', views.join, name='join'),
    path('join_success/', views.join_success, name='join_success'),
    path('community/', views.community, name='community'),
    path('api/chat/', views.api_chat_message, name='api_chat_message'),
    path('dashboard/',views.dashboard, name='dashboard'),
]