from django.db import models
from accounts.models import CustomUser
from models_app.models import TrainedModel

class Prediction(models.Model):
    SAFETY_CHOICES = (
        ('safe', 'Safe'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    model_used = models.ForeignKey(TrainedModel, on_delete=models.SET_NULL, null=True)
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
    predicted_hic = models.FloatField(null=True, blank=True)
    safety_status = models.CharField(max_length=10, choices=SAFETY_CHOICES, blank=True)
    safety_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction #{self.id} by {self.user.username} - HIC: {self.predicted_hic}"