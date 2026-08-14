from django.contrib import admin
from .models import Dataset, DatasetRecord

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_type', 'total_records', 'status', 'is_preprocessed', 'uploaded_at']
    list_filter = ['status', 'is_preprocessed', 'file_type']
    search_fields = ['name']

@admin.register(DatasetRecord)
class DatasetRecordAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'hic_value', 'impact_velocity', 'created_at']
    list_filter = ['dataset']