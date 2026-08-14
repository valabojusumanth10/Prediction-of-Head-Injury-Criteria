from django.contrib import admin
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'predicted_hic', 'safety_status', 'created_at']
    list_filter = ['safety_status']
    search_fields = ['user__username']