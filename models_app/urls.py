from django.urls import path
from . import views

app_name = 'models_app'

urlpatterns = [
    path('', views.model_list, name='model_list'),
    path('train/', views.model_train, name='model_train'),
    path('<int:pk>/', views.model_detail, name='model_detail'),
    path('<int:pk>/delete/', views.model_delete, name='model_delete'),
    path('<int:pk>/evaluate/', views.model_evaluate, name='model_evaluate'),
    path('<int:pk>/activate/', views.set_active_model, name='set_active_model'),
]