import numpy as np
import pickle
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from .models import Prediction
from .forms import PredictionForm
from models_app.models import TrainedModel

@login_required
def predict(request):
    form = PredictionForm(request.POST or None)
    active_model = TrainedModel.objects.filter(is_active=True, status='trained').first()

    if request.method == 'POST' and form.is_valid():
        if not active_model:
            messages.error(request, 'No trained model available. Please contact admin.')
            return redirect('predictions:predict')

        prediction = form.save(commit=False)
        prediction.user = request.user
        prediction.model_used = active_model

        try:
            scaler_path = os.path.join(settings.MEDIA_ROOT, str(active_model.scaler_file))
            model_path  = os.path.join(settings.MEDIA_ROOT, str(active_model.model_file))

            with open(scaler_path, 'rb') as f: scaler   = pickle.load(f)
            with open(model_path,  'rb') as f: ml_model = pickle.load(f)

            features = np.array([[
                prediction.hood_length,     prediction.hood_width,      prediction.hood_thickness,
                prediction.material_density, prediction.youngs_modulus,  prediction.poisson_ratio,
                prediction.yield_strength,  prediction.impact_velocity,  prediction.impact_angle,
                prediction.hood_mass,        prediction.stiffness,        prediction.energy_absorption
            ]])
            features_scaled = scaler.transform(features)
            hic_pred = float(ml_model.predict(features_scaled)[0])
            prediction.predicted_hic = round(hic_pred, 2)

            if hic_pred < 1000:
                prediction.safety_status   = 'safe'
                prediction.safety_feedback = (
                    f'HIC value of {hic_pred:.2f} is within the safe limit (< 1000). '
                    'This hood design meets pedestrian head injury protection requirements '
                    'per EURO NCAP and FMVSS 201 standards. No redesign is required.'
                )
            elif hic_pred < 1500:
                prediction.safety_status   = 'warning'
                prediction.safety_feedback = (
                    f'HIC value of {hic_pred:.2f} is in the warning zone (1000–1500). '
                    'The design is borderline. Consider increasing hood thickness, '
                    'improving energy absorption structures, or using a lower-density material '
                    'to bring the HIC below 1000.'
                )
            else:
                prediction.safety_status   = 'danger'
                prediction.safety_feedback = (
                    f'HIC value of {hic_pred:.2f} exceeds the danger threshold (> 1500). '
                    'This hood design poses a serious pedestrian head injury risk. '
                    'Immediate redesign is required. Focus on increasing energy absorption, '
                    'reducing stiffness, and adjusting material properties.'
                )
            prediction.save()
            messages.success(request, f'Prediction complete! Predicted HIC = {hic_pred:.2f}')
            return redirect('predictions:prediction_result', pk=prediction.pk)

        except FileNotFoundError:
            messages.error(request, 'Model files not found. Please ask admin to retrain the model.')
        except Exception as e:
            messages.error(request, f'Prediction error: {str(e)}')

    return render(request, 'predictions/predict.html', {
        'form': form,
        'active_model': active_model,
    })

@login_required
def prediction_result(request, pk):
    if request.user.role == 'admin':
        prediction = get_object_or_404(Prediction, pk=pk)
    else:
        prediction = get_object_or_404(Prediction, pk=pk, user=request.user)
    return render(request, 'predictions/prediction_result.html', {'prediction': prediction})

@login_required
def prediction_history(request):
    if request.user.role == 'admin':
        predictions_qs = Prediction.objects.all().order_by('-created_at')
    else:
        predictions_qs = Prediction.objects.filter(user=request.user).order_by('-created_at')

    # Safety filter
    safety_filter = request.GET.get('safety', '')
    if safety_filter in ['safe', 'warning', 'danger']:
        predictions_qs = predictions_qs.filter(safety_status=safety_filter)

    paginator   = Paginator(predictions_qs, 15)
    page_number = request.GET.get('page')
    predictions = paginator.get_page(page_number)

    return render(request, 'predictions/prediction_history.html', {
        'predictions': predictions,
        'safety_filter': safety_filter,
        'total': predictions_qs.count(),
    })

@login_required
def prediction_detail(request, pk):
    if request.user.role == 'admin':
        prediction = get_object_or_404(Prediction, pk=pk)
    else:
        prediction = get_object_or_404(Prediction, pk=pk, user=request.user)
    return render(request, 'predictions/prediction_result.html', {'prediction': prediction})