from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('', views.predict, name='predict'),
    path('result/<int:pk>/', views.prediction_result, name='prediction_result'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('detail/<int:pk>/', views.prediction_detail, name='prediction_detail'),
]