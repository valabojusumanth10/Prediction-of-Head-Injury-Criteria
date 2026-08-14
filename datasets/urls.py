from django.urls import path
from . import views

app_name = 'datasets'

urlpatterns = [
    path('', views.dataset_list, name='dataset_list'),
    path('upload/', views.dataset_upload, name='dataset_upload'),
    path('<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('<int:pk>/delete/', views.dataset_delete, name='dataset_delete'),
    path('<int:pk>/preprocess/', views.preprocess_dataset, name='preprocess_dataset'),
    path('<int:pk>/extract-features/', views.extract_features, name='extract_features'),
]