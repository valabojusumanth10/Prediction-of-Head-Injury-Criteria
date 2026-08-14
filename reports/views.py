import io
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from predictions.models import Prediction
from models_app.models import TrainedModel
from datasets.models import Dataset
from accounts.models import CustomUser
import datetime

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, 'Admin access required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def reports_home(request):
    return render(request, 'reports/reports_home.html')

@login_required
@admin_required
def dataset_report(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'reports/dataset_report.html', {'datasets': datasets})

@login_required
@admin_required
def model_performance_report(request):
    models = TrainedModel.objects.filter(status='trained').order_by('-created_at')
    return render(request, 'reports/model_report.html', {'models': models})

@login_required
def prediction_report(request):
    if request.user.role == 'admin':
        predictions = Prediction.objects.all().order_by('-created_at')
    else:
        predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    safe = predictions.filter(safety_status='safe').count()
    warning = predictions.filter(safety_status='warning').count()
    danger = predictions.filter(safety_status='danger').count()
    return render(request, 'reports/prediction_report.html', {
        'predictions': predictions, 'safe': safe, 'warning': warning, 'danger': danger
    })

@login_required
def download_prediction_report_pdf(request):
    if request.user.role == 'admin':
        predictions = Prediction.objects.all().order_by('-created_at')
    else:
        predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#1a1a2e'),
                                  spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#16213e'),
                                     spaceAfter=4, alignment=TA_CENTER)
    header_style = ParagraphStyle('Header', parent=styles['Normal'],
                                   fontSize=13, textColor=colors.HexColor('#0f3460'),
                                   spaceAfter=6, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Body', parent=styles['Normal'],
                                   fontSize=9, textColor=colors.HexColor('#333333'), spaceAfter=4)

    story = []
    story.append(Paragraph("🚗 HIC Prediction System", title_style))
    story.append(Paragraph("Head Injury Criteria — Prediction Report", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e94560')))
    story.append(Spacer(1, 0.3*cm))

    safe_c = predictions.filter(safety_status='safe').count()
    warn_c = predictions.filter(safety_status='warning').count()
    danger_c = predictions.filter(safety_status='danger').count()
    story.append(Paragraph("Summary Statistics", header_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Predictions', str(predictions.count())],
        ['Safe (HIC < 1000)', str(safe_c)],
        ['Warning (1000–1500)', str(warn_c)],
        ['Danger (HIC > 1500)', str(danger_c)],
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Prediction Records", header_style))
    table_data = [['#', 'User', 'HIC Value', 'Safety', 'Date']]
    for i, p in enumerate(predictions, 1):
        status_text = {'safe': 'SAFE', 'warning': 'WARNING', 'danger': 'DANGER'}.get(p.safety_status, 'N/A')
        table_data.append([
            str(i),
            p.user.get_full_name() or p.user.username,
            f"{p.predicted_hic:.2f}" if p.predicted_hic else 'N/A',
            status_text,
            p.created_at.strftime('%Y-%m-%d'),
        ])
    col_widths = [1.2*cm, 5*cm, 3.5*cm, 3.5*cm, 3.5*cm]
    pred_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    row_colors = []
    for i, p in enumerate(predictions, 1):
        color = colors.HexColor('#d4edda') if p.safety_status == 'safe' else \
                colors.HexColor('#fff3cd') if p.safety_status == 'warning' else \
                colors.HexColor('#f8d7da')
        row_colors.append(('BACKGROUND', (0, i), (-1, i), color))

    pred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e94560')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ] + row_colors))
    story.append(pred_table)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="HIC_Prediction_Report.pdf"'
    return response

@login_required
@admin_required
def download_model_report_pdf(request):
    models = TrainedModel.objects.filter(status='trained').order_by('-created_at')
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#1a1a2e'),
                                  spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#16213e'),
                                     spaceAfter=4, alignment=TA_CENTER)
    header_style = ParagraphStyle('H', parent=styles['Normal'],
                                   fontSize=13, textColor=colors.HexColor('#0f3460'),
                                   spaceAfter=6, fontName='Helvetica-Bold')

    story = []
    story.append(Paragraph("🚗 HIC Prediction System", title_style))
    story.append(Paragraph("Model Performance Report", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e94560')))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Trained Models Performance", header_style))

    table_data = [['Model Name', 'MSE', 'RMSE', 'MAE', 'R²', 'Accuracy', 'Status']]
    for m in models:
        table_data.append([
            m.name[:20],
            f"{m.mse:.4f}" if m.mse else 'N/A',
            f"{m.rmse:.4f}" if m.rmse else 'N/A',
            f"{m.mae:.4f}" if m.mae else 'N/A',
            f"{m.r2_score:.4f}" if m.r2_score else 'N/A',
            f"{m.accuracy:.2f}%" if m.accuracy else 'N/A',
            'Active' if m.is_active else 'Inactive',
        ])
    col_widths = [4.5*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.5*cm, 2.5*cm]
    model_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(model_table)
    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="HIC_Model_Report.pdf"'
    return response

@login_required
@admin_required
def download_dataset_report_pdf(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#1a1a2e'),
                                  spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('S', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#16213e'),
                                     spaceAfter=4, alignment=TA_CENTER)
    header_style = ParagraphStyle('H', parent=styles['Normal'],
                                   fontSize=13, textColor=colors.HexColor('#0f3460'),
                                   spaceAfter=6, fontName='Helvetica-Bold')

    story = []
    story.append(Paragraph("🚗 HIC Prediction System", title_style))
    story.append(Paragraph("Dataset Report", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e94560')))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Dataset Overview", header_style))

    table_data = [['Name', 'Type', 'Total Records', 'Processed', 'Status', 'Uploaded']]
    for d in datasets:
        table_data.append([
            d.name[:25],
            d.file_type.upper(),
            str(d.total_records),
            str(d.processed_records),
            d.status.capitalize(),
            d.uploaded_at.strftime('%Y-%m-%d'),
        ])
    col_widths = [5.5*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm, 3*cm]
    ds_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ds_table)
    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="HIC_Dataset_Report.pdf"'
    return response