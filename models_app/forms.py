from django import forms
from .models import TrainedModel
from datasets.models import Dataset

ACTIVATION_CHOICES = [
    ('relu', 'ReLU'),
    ('sigmoid', 'Sigmoid'),
    ('tanh', 'Tanh'),
    ('linear', 'Linear'),
    ('elu', 'ELU'),
]

class ModelTrainingForm(forms.ModelForm):
    activation_function = forms.ChoiceField(choices=ACTIVATION_CHOICES,
                                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = TrainedModel
        fields = ['name', 'description', 'dataset', 'num_layers', 'activation_function',
                  'learning_rate', 'epochs', 'batch_size', 'test_size']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'dataset': forms.Select(attrs={'class': 'form-control'}),
            'num_layers': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 10}),
            'learning_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'epochs': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 1000}),
            'batch_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'test_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.05', 'min': '0.1', 'max': '0.5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dataset'].queryset = Dataset.objects.filter(is_preprocessed=True)