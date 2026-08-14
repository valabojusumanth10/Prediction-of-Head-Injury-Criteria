from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:pk>/update/', views.admin_user_update, name='admin_user_update'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:pk>/toggle/', views.toggle_user_status, name='toggle_user_status'),
]