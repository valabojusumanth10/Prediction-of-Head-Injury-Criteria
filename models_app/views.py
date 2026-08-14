import numpy as np
import pickle
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import TrainedModel
from .forms import ModelTrainingForm
from datasets.models import DatasetRecord

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, 'Admin access required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@login_required
@admin_required
def model_list(request):
    models = TrainedModel.objects.all().order_by('-created_at')
    return render(request, 'models_app/model_list.html', {'models': models})

@login_required
@admin_required
def model_train(request):
    form = ModelTrainingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        model_obj = form.save(commit=False)
        model_obj.trained_by = request.user
        model_obj.status = 'training'
        model_obj.save()

        try:
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

            records = DatasetRecord.objects.filter(dataset=model_obj.dataset)

            if records.count() < 10:
                raise Exception("Not enough data records to train. Need at least 10.")

            X, y = [], []

            for r in records:
                X.append([
                    r.hood_length or 0,
                    r.hood_width or 0,
                    r.hood_thickness or 0,
                    r.material_density or 0,
                    r.youngs_modulus or 0,
                    r.poisson_ratio or 0,
                    r.yield_strength or 0,
                    r.impact_velocity or 0,
                    r.impact_angle or 0,
                    r.hood_mass or 0,
                    r.stiffness or 0,
                    r.energy_absorption or 0
                ])
                y.append(r.hic_value or 0)

            X = np.array(X)
            y = np.array(y)

            # Train Test Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=model_obj.test_size,
                random_state=42
            )

            # Scaling
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            act = model_obj.activation_function
            if act == 'linear':
                act = 'identity'

            hidden_layers = tuple([64] * model_obj.num_layers)

            clf = MLPRegressor(
                hidden_layer_sizes=hidden_layers,
                activation=act,
                learning_rate_init=model_obj.learning_rate,
                max_iter=model_obj.epochs,
                batch_size=min(model_obj.batch_size, len(X_train)),
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=20
            )

            # Train model
            clf.fit(X_train_scaled, y_train)

            # Predictions
            y_pred = clf.predict(X_test_scaled)

            # Metrics
            mse_val = mean_squared_error(y_test, y_pred)
            rmse_val = float(np.sqrt(mse_val))
            mae_val = float(mean_absolute_error(y_test, y_pred))
            r2_val = float(r2_score(y_test, y_pred))

            # Handle correlation safely
            corr_matrix = np.corrcoef(y_test, y_pred)
            corr_val = float(np.nan_to_num(corr_matrix[0, 1]))

            acc = max(0.0, float(r2_val * 100))

            # Create directories
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'models'), exist_ok=True)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'scalers'), exist_ok=True)

            model_path = f'models/model_{model_obj.id}.pkl'
            scaler_path = f'scalers/scaler_{model_obj.id}.pkl'

            # Save model
            with open(os.path.join(settings.MEDIA_ROOT, model_path), 'wb') as f:
                pickle.dump(clf, f)

            with open(os.path.join(settings.MEDIA_ROOT, scaler_path), 'wb') as f:
                pickle.dump(scaler, f)

            # Save metrics
            model_obj.mse = round(mse_val, 6)
            model_obj.rmse = round(rmse_val, 6)
            model_obj.mae = round(mae_val, 6)
            model_obj.r2_score = round(r2_val, 6)
            model_obj.correlation = round(corr_val, 6)
            model_obj.accuracy = round(acc, 2)

            model_obj.model_file = model_path
            model_obj.scaler_file = scaler_path

            model_obj.status = 'trained'

            model_obj.training_log = (
                f"Training completed successfully.\n"
                f"Training samples: {len(X_train)}\n"
                f"Testing samples: {len(X_test)}\n"
                f"MSE: {mse_val:.6f}\n"
                f"RMSE: {rmse_val:.6f}\n"
                f"MAE: {mae_val:.6f}\n"
                f"R2 Score: {r2_val:.6f}\n"
                f"Correlation: {corr_val:.6f}\n"
                f"Accuracy: {acc:.2f}%"
            )

            model_obj.save()

            # Set active model
            TrainedModel.objects.exclude(pk=model_obj.pk).update(is_active=False)
            model_obj.is_active = True
            model_obj.save()

            messages.success(
                request,
                f'Model trained successfully! Accuracy: {acc:.2f}%'
            )

        except Exception as e:

            model_obj.status = 'failed'
            model_obj.training_log = str(e)
            model_obj.save()

            messages.error(
                request,
                f'Training failed: {str(e)}'
            )

        return redirect('models_app:model_list')

    return render(request, 'models_app/model_train.html', {'form': form})

@login_required
@admin_required
def model_detail(request, pk):
    model_obj = get_object_or_404(TrainedModel, pk=pk)
    # Build metrics list for template display
    model_metrics = []
    if model_obj.status == 'trained':
        model_metrics = [
            ('Accuracy',    f"{model_obj.accuracy:.2f}%"    if model_obj.accuracy    is not None else 'N/A', '#2e7d32'),
            ('MSE',         f"{model_obj.mse:.6f}"          if model_obj.mse         is not None else 'N/A', '#e94560'),
            ('RMSE',        f"{model_obj.rmse:.6f}"         if model_obj.rmse        is not None else 'N/A', '#e65100'),
            ('MAE',         f"{model_obj.mae:.6f}"          if model_obj.mae         is not None else 'N/A', '#1565c0'),
            ('R² Score',    f"{model_obj.r2_score:.6f}"     if model_obj.r2_score    is not None else 'N/A', '#00695c'),
            ('Correlation', f"{model_obj.correlation:.6f}"  if model_obj.correlation is not None else 'N/A', '#6a1b9a'),
        ]
    return render(request, 'models_app/model_detail.html', {
        'model': model_obj,
        'model_metrics': model_metrics,
    })

@login_required
@admin_required
def model_evaluate(request, pk):
    """Dedicated model evaluation page — FR: Admin can evaluate trained model"""
    model_obj = get_object_or_404(TrainedModel, pk=pk)
    evaluation_data = None

    if model_obj.status == 'trained' and model_obj.model_file and model_obj.scaler_file:
        try:
            import pickle, numpy as np
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            from datasets.models import DatasetRecord

            model_path  = os.path.join(settings.MEDIA_ROOT, str(model_obj.model_file))
            scaler_path = os.path.join(settings.MEDIA_ROOT, str(model_obj.scaler_file))

            with open(model_path,  'rb') as f: clf    = pickle.load(f)
            with open(scaler_path, 'rb') as f: scaler = pickle.load(f)

            records = DatasetRecord.objects.filter(dataset=model_obj.dataset)
            X, y = [], []
            for r in records:
                X.append([r.hood_length, r.hood_width, r.hood_thickness,
                          r.material_density, r.youngs_modulus, r.poisson_ratio,
                          r.yield_strength, r.impact_velocity, r.impact_angle,
                          r.hood_mass, r.stiffness, r.energy_absorption])
                y.append(r.hic_value)

            X_s   = scaler.transform(np.array(X))
            y_pred = clf.predict(X_s)
            y_true = np.array(y)

            mse_v  = float(mean_squared_error(y_true, y_pred))
            rmse_v = float(np.sqrt(mse_v))
            mae_v  = float(mean_absolute_error(y_true, y_pred))
            r2_v   = float(r2_score(y_true, y_pred))
            corr_v = float(np.corrcoef(y_true, y_pred)[0, 1])
            acc_v  = max(0.0, float(r2_v * 100))

            # Sample 20 actual vs predicted pairs for display
            indices = np.random.choice(len(y_true), min(20, len(y_true)), replace=False)
            pairs = [(round(float(y_true[i]), 2), round(float(y_pred[i]), 2),
                      round(abs(float(y_true[i]) - float(y_pred[i])), 2))
                     for i in sorted(indices)]

            evaluation_data = {
                'mse': round(mse_v, 6),
                'rmse': round(rmse_v, 6),
                'mae': round(mae_v, 6),
                'r2': round(r2_v, 6),
                'correlation': round(corr_v, 6),
                'accuracy': round(acc_v, 2),
                'total_samples': len(y_true),
                'pairs': pairs,
            }
        except Exception as e:
            messages.error(request, f'Evaluation error: {str(e)}')

    return render(request, 'models_app/model_evaluate.html', {
        'model': model_obj,
        'evaluation_data': evaluation_data,
    })

@login_required
@admin_required
def model_delete(request, pk):
    model_obj = get_object_or_404(TrainedModel, pk=pk)
    if request.method == 'POST':
        # Delete model files from disk
        for fld in ['model_file', 'scaler_file']:
            fpath = getattr(model_obj, fld)
            if fpath:
                full = os.path.join(settings.MEDIA_ROOT, str(fpath))
                if os.path.exists(full):
                    os.remove(full)
        model_obj.delete()
        messages.success(request, 'Model deleted successfully.')
        return redirect('models_app:model_list')
    return render(request, 'models_app/model_confirm_delete.html', {'model': model_obj})

@login_required
@admin_required
def set_active_model(request, pk):
    model_obj = get_object_or_404(TrainedModel, pk=pk)
    if model_obj.status != 'trained':
        messages.error(request, 'Only trained models can be set as active.')
        return redirect('models_app:model_list')
    TrainedModel.objects.all().update(is_active=False)
    model_obj.is_active = True
    model_obj.save()
    messages.success(request, f'"{model_obj.name}" is now the active prediction model.')
    return redirect('models_app:model_list')