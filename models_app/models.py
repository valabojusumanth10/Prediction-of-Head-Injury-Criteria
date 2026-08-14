from django.db import models
from accounts.models import CustomUser
from datasets.models import Dataset

class TrainedModel(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('training', 'Training'),
        ('trained', 'Trained'),
        ('failed', 'Failed'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)
    num_layers = models.IntegerField(default=4)
    activation_function = models.CharField(max_length=50, default='relu')
    learning_rate = models.FloatField(default=0.001)
    epochs = models.IntegerField(default=100)
    batch_size = models.IntegerField(default=32)
    test_size = models.FloatField(default=0.2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mse = models.FloatField(null=True, blank=True)
    rmse = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)
    r2_score = models.FloatField(null=True, blank=True)
    correlation = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    model_file = models.FileField(upload_to='models/', blank=True, null=True)
    scaler_file = models.FileField(upload_to='scalers/', blank=True, null=True)
    training_log = models.TextField(blank=True)
    trained_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.status})"