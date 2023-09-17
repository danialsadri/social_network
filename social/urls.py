from django.urls import path
from . import views

app_name = 'social'
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('edit/user/', views.edit_user, name='edit_user'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('ticket/', views.ticket, name='ticket'),
]
