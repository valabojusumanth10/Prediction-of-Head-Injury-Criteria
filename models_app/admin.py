from django.contrib import admin
from .models import TrainedModel

@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'accuracy', 'mse', 'r2_score', 'is_active', 'created_at']
    list_filter = ['status', 'is_active']
    search_fields = ['name']