from django.db import models
from accounts.models import CustomUser

class Dataset(models.Model):
    STATUS_CHOICES = (
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('error', 'Error'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='datasets/')
    file_type = models.CharField(max_length=10)
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_preprocessed = models.BooleanField(default=False)
    is_features_extracted = models.BooleanField(default=False)
    preprocessing_notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

class DatasetRecord(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='records')
    hood_length = models.FloatField()
    hood_width = models.FloatField()
    hood_thickness = models.FloatField()
    material_density = models.FloatField()
    youngs_modulus = models.FloatField()
    poisson_ratio = models.FloatField()
    yield_strength = models.FloatField()
    impact_velocity = models.FloatField()
    impact_angle = models.FloatField()
    hood_mass = models.FloatField()
    stiffness = models.FloatField()
    energy_absorption = models.FloatField()
    hic_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record {self.id} - HIC: {self.hic_value}"