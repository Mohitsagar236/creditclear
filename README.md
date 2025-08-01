# Credit Risk Assessment System

A comprehensive machine learning system for credit risk assessment featuring XGBoost and LightGBM models with a modern React dashboard and FastAPI backend.

## 🌟 Features

- **Advanced ML Models**: XGBoost and LightGBM with imbalanced data handling
- **Feature Engineering**: Polynomial features and financial ratio calculations
- **Model Tracking**: MLflow integration for experiment tracking
- **Explainable AI**: SHAP values for model interpretability
- **Async Processing**: Celery-based background task processing
- **Modern Dashboard**: React-based UI with real-time predictions
- **REST API**: FastAPI backend with automatic documentation
- **Data Processing**: Comprehensive data cleaning and validation

## 🏗️ Architecture

```plaintext
credit-risk-model/
├── data/
│   ├── raw/         # Original, immutable data
│   ├── processed/   # Cleaned and processed data
│   └── synthetic/   # Generated synthetic data
├── notebooks/
│   ├── eda.ipynb              # Exploratory Data Analysis
│   ├── feature_selection.ipynb # Feature Selection Analysis
│   └── model_evaluation.ipynb  # Model Evaluation and Comparison
├── src/
│   ├── api/          # FastAPI implementation
│   ├── data_processing/
│   ├── models/       # Model implementations
│   ├── utils/        # Utility functions
│   └── dashboard/    # Web dashboard components
└── tests/            # Test suite
```

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Docker Setup:

```bash
docker-compose up
```

## Development

- Access Jupyter Lab at [http://localhost:8888](http://localhost:8888)
- Access API at [http://localhost:8000](http://localhost:8000)
- API Documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

## Notebooks

1. `eda.ipynb`: Exploratory Data Analysis
   - Data quality assessment
   - Distribution analysis
   - Correlation studies
   - Missing value analysis

2. `feature_selection.ipynb`: Feature Selection
   - Correlation-based selection
   - Feature importance analysis
   - Statistical tests
   - Dimensionality reduction

3. `model_evaluation.ipynb`: Model Evaluation
   - Model comparison
   - Performance metrics
   - Cross-validation results
   - Feature importance
   - Model interpretation

## License

MIT
