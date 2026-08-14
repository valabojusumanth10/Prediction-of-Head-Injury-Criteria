from django import forms
from .models import Prediction

class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = [
            'hood_length', 'hood_width', 'hood_thickness',
            'material_density', 'youngs_modulus', 'poisson_ratio',
            'yield_strength', 'impact_velocity', 'impact_angle',
            'hood_mass', 'stiffness', 'energy_absorption',
        ]
        labels = {
            'hood_length': 'Hood Length (mm)',
            'hood_width': 'Hood Width (mm)',
            'hood_thickness': 'Hood Thickness (mm)',
            'material_density': 'Material Density (kg/m³)',
            'youngs_modulus': "Young's Modulus (GPa)",
            'poisson_ratio': "Poisson's Ratio",
            'yield_strength': 'Yield Strength (MPa)',
            'impact_velocity': 'Impact Velocity (m/s)',
            'impact_angle': 'Impact Angle (°)',
            'hood_mass': 'Hood Mass (kg)',
            'stiffness': 'Stiffness (N/m)',
            'energy_absorption': 'Energy Absorption (J)',
        }
        widgets = {
            'hood_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1200', 'step': '0.01'}),
            'hood_width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1500', 'step': '0.01'}),
            'hood_thickness': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0.8', 'step': '0.001'}),
            'material_density': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2700', 'step': '0.01'}),
            'youngs_modulus': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 70', 'step': '0.01'}),
            'poisson_ratio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0.33', 'step': '0.001'}),
            'yield_strength': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 250', 'step': '0.01'}),
            'impact_velocity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9.7', 'step': '0.01'}),
            'impact_angle': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 65', 'step': '0.01'}),
            'hood_mass': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12', 'step': '0.01'}),
            'stiffness': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50000', 'step': '0.01'}),
            'energy_absorption': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 800', 'step': '0.01'}),
        }