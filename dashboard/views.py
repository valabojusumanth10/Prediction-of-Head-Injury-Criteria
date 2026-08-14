from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from predictions.models import Prediction
from models_app.models import TrainedModel
from datasets.models import Dataset
from accounts.models import CustomUser

@login_required
def home(request):
    user = request.user
    context = {}
    if user.role == 'admin':
        context['total_users'] = CustomUser.objects.filter(role='user').count()
        context['total_datasets'] = Dataset.objects.count()
        context['total_models'] = TrainedModel.objects.filter(status='trained').count()
        context['total_predictions'] = Prediction.objects.count()
        context['active_model'] = TrainedModel.objects.filter(is_active=True).first()
        context['recent_predictions'] = Prediction.objects.order_by('-created_at')[:5]
        context['safe_count'] = Prediction.objects.filter(safety_status='safe').count()
        context['warning_count'] = Prediction.objects.filter(safety_status='warning').count()
        context['danger_count'] = Prediction.objects.filter(safety_status='danger').count()
    else:
        context['my_predictions'] = Prediction.objects.filter(user=user).count()
        context['active_model'] = TrainedModel.objects.filter(is_active=True).first()
        context['recent_predictions'] = Prediction.objects.filter(user=user).order_by('-created_at')[:5]
        context['safe_count'] = Prediction.objects.filter(user=user, safety_status='safe').count()
        context['warning_count'] = Prediction.objects.filter(user=user, safety_status='warning').count()
        context['danger_count'] = Prediction.objects.filter(user=user, safety_status='danger').count()
    return render(request, 'dashboard/home.html', context)