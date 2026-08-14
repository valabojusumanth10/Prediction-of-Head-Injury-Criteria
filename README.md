# 🧠 Prediction of Head Injury Criteria (HIC)

A full-stack machine learning web application for predicting the **Head Injury Criterion (HIC)** of vehicle hood designs and evaluating their potential pedestrian head-injury risk.

The system combines a Django-based web application with a machine learning pipeline, allowing users to manage datasets, train and evaluate models, generate HIC predictions, and view prediction history and reports through a web interface.

The project was developed as an end-to-end academic project combining **machine learning, data processing, backend development, database integration, authentication, and web-based prediction**.

---

## 🚀 Key Features

### 🤖 HIC Prediction

- Predicts HIC values using a trained machine learning model
- Accepts multiple vehicle hood and material parameters as inputs
- Automatically scales input features before prediction
- Generates a predicted HIC value
- Provides an interpreted safety classification

### 🛡️ Safety Classification

Predictions are categorized into three levels:

```text
                Predicted HIC
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       < 1000     1000–1500    > 1500
          │          │          │
        SAFE       WARNING     DANGER

📊 Dataset Management
Upload and manage datasets
View dataset information
Store datasets through the application
Manage dataset records through the Django backend
🧠 Machine Learning Model Management
Create and manage trained models
Configure training parameters
Track model training status
Store trained model files
Store feature scaler files
Maintain training logs
Activate trained models for prediction
📈 Model Evaluation

The system tracks multiple evaluation metrics, including:

Mean Squared Error (MSE)
Root Mean Squared Error (RMSE)
Mean Absolute Error (MAE)
R² Score
Correlation
Accuracy
👤 User Authentication
User registration
Login and logout
Custom user model
Role-based access
Protected prediction functionality
User-specific prediction history
📜 Prediction History
Store previous predictions
View prediction results
Filter predictions by safety status
Paginated prediction history
Admin access to prediction records
📑 Reports

The project includes dedicated report functionality for:

Dataset reports
Model reports
Prediction reports
Report dashboard
📊 Dashboard

A dedicated dashboard provides access to the major parts of the system, including datasets, models, predictions, and reports.

🔬 Prediction Inputs

The prediction system uses the following parameters:

Parameter	Description
Hood Length	Length of the vehicle hood
Hood Width	Width of the vehicle hood
Hood Thickness	Hood thickness
Material Density	Density of the hood material
Young's Modulus	Material stiffness property
Poisson Ratio	Material deformation property
Yield Strength	Material strength
Impact Velocity	Impact velocity
Impact Angle	Impact angle
Hood Mass	Mass of the hood
Stiffness	Hood structural stiffness
Energy Absorption	Energy absorption characteristic

These features are passed through the stored scaler before being provided to the active trained model.

🔄 Complete System Workflow
                    ┌──────────────────┐
                    │      User        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Authentication   │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌────────────────┐      ┌─────────────────┐
        │ Dataset Module │      │ Prediction      │
        │                │      │ Module          │
        └───────┬────────┘      └────────┬────────┘
                │                        │
                ▼                        ▼
        ┌────────────────┐      ┌─────────────────┐
        │ Model Training │─────▶│ Active ML Model │
        └───────┬────────┘      └────────┬────────┘
                │                        │
                ▼                        ▼
        ┌────────────────┐      ┌─────────────────┐
        │ Model          │      │ HIC Prediction  │
        │ Evaluation     │      └────────┬────────┘
        └────────────────┘               │
                                         ▼
                              ┌────────────────────┐
                              │ Safety Assessment  │
                              │                    │
                              │ Safe / Warning /   │
                              │ Danger             │
                              └─────────┬──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ Prediction History │
                              │ & Reports          │
                              └────────────────────┘
🛠️ Tech Stack
Backend
Python
Django 4.2
Django REST Framework
Django Crispy Forms
MySQL
Machine Learning & Data Science
TensorFlow
Keras
Scikit-learn
NumPy
Pandas
SciPy
Joblib
OpenPyXL
Frontend
Django Templates
HTML
CSS
JavaScript
Bootstrap 5
Crispy Forms
Supporting Technologies
Python Pickle
Pillow
Matplotlib
Seaborn
OpenCV
Python-dotenv

The repository's dependency file includes Django, Django REST Framework, MySQL support, NumPy, Pandas, Scikit-learn, TensorFlow/Keras and other supporting packages used by the application.

📂 Project Structure
Prediction-of-Head-Injury-Criteria/
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── dashboard/
│   ├── views.py
│   └── urls.py
│
├── datasets/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── models_app/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── predictions/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── reports/
│   ├── views.py
│   └── urls.py
│
├── hic_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
│   ├── accounts/
│   ├── dashboard/
│   ├── datasets/
│   ├── models_app/
│   ├── predictions/
│   └── reports/
│
├── Sample_Datasets/
├── Screenshots/
│
├── generate_dataset.py
├── manage.py
├── requirements.txt
├── HIC_Dataset_Report.pdf
├── HIC_Model_Report.pdf
└── hic_project_process.txt
⚙️ Installation & Setup
1. Clone the Repository
git clone https://github.com/valabojusumanth10/Prediction-of-Head-Injury-Criteria.git

cd Prediction-of-Head-Injury-Criteria
2. Create a Virtual Environment
python -m venv hic_env

Activate it on Windows:

hic_env\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure MySQL

Create a MySQL database for the project.

Update the Django database configuration in:

hic_project/settings.py

with your local MySQL credentials.

Do not commit real database passwords or secret keys to a public repository.

5. Run Migrations
python manage.py makemigrations
python manage.py migrate
6. Create an Admin User
python manage.py createsuperuser
7. Start the Development Server
python manage.py runserver

The application will be available at:

http://127.0.0.1:8000/
🧪 Prediction Process

Once a trained model is available:

1. Login
      ↓
2. Open Prediction Module
      ↓
3. Enter Hood & Material Parameters
      ↓
4. Validate Input
      ↓
5. Load Active Model
      ↓
6. Load Feature Scaler
      ↓
7. Scale Input Features
      ↓
8. Generate HIC Prediction
      ↓
9. Determine Safety Status
      ↓
10. Store Prediction
      ↓
11. Display Result

The implementation loads the active trained model and scaler, constructs the feature vector from the prediction form, scales the values, generates the HIC prediction, stores the result, and displays the corresponding safety assessment.

📊 Model Management

The application provides a model-management layer where trained models can be associated with datasets and tracked through different states:

Pending
   ↓
Training
   ↓
Trained
   │
   └── Failed

Model configurations include parameters such as:

Number of layers
Activation function
Learning rate
Epochs
Batch size
Test size

The system also stores model files, scaler files, training logs and evaluation metrics.

📸 Screenshots

The repository includes screenshots demonstrating the working application.

🔐 Authentication

📊 Dashboard

📂 Dataset Management

🧠 Model Management

🔮 HIC Prediction

📈 Prediction Result

📜 Prediction History

Additional application screenshots are available in the Screenshots/ directory.

📄 Project Documentation

The repository also contains detailed project documentation:

HIC_Dataset_Report.pdf
HIC_Model_Report.pdf
hic_project_process.txt

These documents provide additional information about the dataset, model and development process.

🎯 What This Project Demonstrates

This project demonstrates practical experience with:

Full-stack Django development
Machine learning integration
Data preprocessing
Model training and evaluation
Regression-based prediction workflow
MySQL database integration
User authentication
Role-based application functionality
Dataset management
Model management
Prediction history
Report generation
Web-based ML deployment
Form validation
File handling
Building an end-to-end ML application
⚠️ Disclaimer

This project is an academic/educational machine learning application.

The HIC predictions and safety classifications produced by the application should not be treated as a substitute for certified automotive safety testing, engineering simulation, regulatory testing, or professional safety assessment.

👨‍💻 Author

Sumanth Valaboju

B.Tech Computer Science Engineering
Full-Stack Developer | Machine Learning Enthusiast

GitHub:
https://github.com/valabojusumanth10
