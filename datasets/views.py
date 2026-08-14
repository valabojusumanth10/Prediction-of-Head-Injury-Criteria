import pandas as pd
import numpy as np
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Dataset, DatasetRecord
from .forms import DatasetUploadForm

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            from django.contrib import messages
            messages.error(request, 'Admin access required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__   # ← THIS LINE IS REQUIRED
    return wrapper

@login_required
@admin_required
def dataset_list(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'datasets/dataset_list.html', {'datasets': datasets})

@login_required
@admin_required
def dataset_upload(request):
    form = DatasetUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        dataset = form.save(commit=False)
        dataset.uploaded_by = request.user
        file_ext = os.path.splitext(form.cleaned_data['file'].name)[1].lower()
        dataset.file_type = file_ext.replace('.', '')
        dataset.save()
        try:
            if file_ext in ['.csv']:
                df = pd.read_csv(dataset.file.path)
            else:
                df = pd.read_excel(dataset.file.path)
            dataset.total_records = len(df)
            dataset.status = 'uploaded'
            dataset.save()
            messages.success(request, f'Dataset uploaded with {len(df)} records!')
        except Exception as e:
            dataset.status = 'error'
            dataset.save()
            messages.error(request, f'Error reading file: {str(e)}')
        return redirect('datasets:dataset_list')
    return render(request, 'datasets/dataset_upload.html', {'form': form})

@login_required
@admin_required
def dataset_detail(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    records = dataset.records.all()[:20]
    return render(request, 'datasets/dataset_detail.html', {'dataset': dataset, 'records': records})

@login_required
@admin_required
def dataset_delete(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    if request.method == 'POST':
        if os.path.exists(dataset.file.path):
            os.remove(dataset.file.path)
        dataset.delete()
        messages.success(request, 'Dataset deleted successfully!')
        return redirect('datasets:dataset_list')
    return render(request, 'datasets/dataset_confirm_delete.html', {'dataset': dataset})

@login_required
@admin_required
def preprocess_dataset(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    try:
        file_ext = os.path.splitext(dataset.file.name)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(dataset.file.path)
        else:
            df = pd.read_excel(dataset.file.path)

        initial_count = len(df)
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[~((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR)))]

        required_cols = ['hood_length', 'hood_width', 'hood_thickness', 'material_density',
                         'youngs_modulus', 'poisson_ratio', 'yield_strength', 'impact_velocity',
                         'impact_angle', 'hood_mass', 'stiffness', 'energy_absorption', 'hic_value']

        col_map = {}
        for rc in required_cols:
            for dc in df.columns:
                if rc.lower().replace('_', '') in dc.lower().replace('_', '').replace(' ', ''):
                    col_map[rc] = dc
                    break

        DatasetRecord.objects.filter(dataset=dataset).delete()
        saved = 0
        for _, row in df.iterrows():
            try:
                DatasetRecord.objects.create(
                    dataset=dataset,
                    hood_length=float(row.get(col_map.get('hood_length', 'hood_length'), row.iloc[0])),
                    hood_width=float(row.get(col_map.get('hood_width', 'hood_width'), row.iloc[1])),
                    hood_thickness=float(row.get(col_map.get('hood_thickness', 'hood_thickness'), row.iloc[2])),
                    material_density=float(row.get(col_map.get('material_density', 'material_density'), row.iloc[3])),
                    youngs_modulus=float(row.get(col_map.get('youngs_modulus', 'youngs_modulus'), row.iloc[4])),
                    poisson_ratio=float(row.get(col_map.get('poisson_ratio', 'poisson_ratio'), row.iloc[5])),
                    yield_strength=float(row.get(col_map.get('yield_strength', 'yield_strength'), row.iloc[6])),
                    impact_velocity=float(row.get(col_map.get('impact_velocity', 'impact_velocity'), row.iloc[7])),
                    impact_angle=float(row.get(col_map.get('impact_angle', 'impact_angle'), row.iloc[8])),
                    hood_mass=float(row.get(col_map.get('hood_mass', 'hood_mass'), row.iloc[9])),
                    stiffness=float(row.get(col_map.get('stiffness', 'stiffness'), row.iloc[10])),
                    energy_absorption=float(row.get(col_map.get('energy_absorption', 'energy_absorption'), row.iloc[11])),
                    hic_value=float(row.get(col_map.get('hic_value', 'hic_value'), row.iloc[12])),
                )
                saved += 1
            except Exception:
                continue

        dataset.is_preprocessed = True
        dataset.status = 'processed'
        dataset.processed_records = saved
        dataset.preprocessing_notes = f"Original: {initial_count}, After cleaning: {saved}"
        dataset.save()
        messages.success(request, f'Preprocessing complete! {saved} records saved.')
    except Exception as e:
        dataset.status = 'error'
        dataset.save()
        messages.error(request, f'Preprocessing error: {str(e)}')
    return redirect('datasets:dataset_detail', pk=pk)

@login_required
@admin_required
def extract_features(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    if not dataset.is_preprocessed:
        messages.warning(request, 'Please preprocess the dataset first.')
        return redirect('datasets:dataset_detail', pk=pk)
    records = dataset.records.all()
    count = records.count()
    dataset.is_features_extracted = True
    dataset.save()
    messages.success(request, f'Feature extraction complete for {count} records!')
    return redirect('datasets:dataset_detail', pk=pk)