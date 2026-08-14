from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('datasets/', views.dataset_report, name='dataset_report'),
    path('models/', views.model_performance_report, name='model_report'),
    path('predictions/', views.prediction_report, name='prediction_report'),
    path('download/predictions/', views.download_prediction_report_pdf, name='download_prediction_pdf'),
    path('download/models/', views.download_model_report_pdf, name='download_model_pdf'),
    path('download/datasets/', views.download_dataset_report_pdf, name='download_dataset_pdf'),
]