"""
Contamination Detection ML Model
Uses Isolation Forest for anomaly detection on bioreactor sensor data
MLflow tracking for model versioning and deployment
"""
# Databricks notebook source
# MAGIC %md
# MAGIC # Contamination Detection Model Training
# MAGIC
# MAGIC **Model Type**: Isolation Forest (Anomaly Detection)
# MAGIC
# MAGIC **Purpose**: Real-time detection of contamination events in bioreactors
# MAGIC
# MAGIC **Features**:
# MAGIC - pH stability and drift patterns
# MAGIC - Temperature variations
# MAGIC - Dissolved oxygen anomalies
# MAGIC - Cell density growth patterns
# MAGIC - Metabolite profiles (glucose, lactate)
# MAGIC
# MAGIC **Performance Target**: <1% false positive rate, >95% recall

# COMMAND ----------

import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set MLflow experiment
mlflow.set_experiment("/Pharma-Digital-Twin/Contamination-Detection")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Training Data

# COMMAND ----------

def generate_contamination_training_data(n_normal=10000, n_contaminated=500):
    """Generate synthetic training data with normal and contaminated batches"""

    np.random.seed(42)

    # Normal bioreactor data
    normal_data = {
        'ph_mean': np.random.normal(7.0, 0.05, n_normal),
        'ph_std': np.random.uniform(0.01, 0.05, n_normal),
        'temp_mean': np.random.normal(37.0, 0.1, n_normal),
        'temp_std': np.random.uniform(0.02, 0.08, n_normal),
        'do_mean': np.random.normal(45, 2, n_normal),
        'do_std': np.random.uniform(1, 3, n_normal),
        'cell_density_growth_rate': np.random.normal(0.3, 0.05, n_normal),
        'glucose_consumption_rate': np.random.normal(0.5, 0.1, n_normal),
        'lactate_production_rate': np.random.normal(0.2, 0.05, n_normal),
        'contaminated': [0] * n_normal
    }

    # Contaminated bioreactor data (anomalous patterns)
    contaminated_data = {
        'ph_mean': np.random.normal(7.3, 0.3, n_contaminated),  # pH shifts
        'ph_std': np.random.uniform(0.1, 0.3, n_contaminated),  # Higher variance
        'temp_mean': np.random.normal(37.0, 0.15, n_contaminated),
        'temp_std': np.random.uniform(0.1, 0.2, n_contaminated),
        'do_mean': np.random.normal(35, 8, n_contaminated),  # DO drops
        'do_std': np.random.uniform(4, 8, n_contaminated),
        'cell_density_growth_rate': np.random.normal(0.15, 0.1, n_contaminated),  # Slower growth
        'glucose_consumption_rate': np.random.normal(0.7, 0.2, n_contaminated),  # Abnormal consumption
        'lactate_production_rate': np.random.normal(0.4, 0.15, n_contaminated),  # Higher lactate
        'contaminated': [1] * n_contaminated
    }

    # Combine datasets
    df_normal = pd.DataFrame(normal_data)
    df_contaminated = pd.DataFrame(contaminated_data)
    df = pd.concat([df_normal, df_contaminated], ignore_index=True)

    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df

# Generate data
df_train = generate_contamination_training_data()
print(f"Training data shape: {df_train.shape}")
print(f"Contamination rate: {df_train['contaminated'].mean():.1%}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train Isolation Forest Model

# COMMAND ----------

# Prepare features
feature_cols = [col for col in df_train.columns if col != 'contaminated']
X = df_train[feature_cols]
y = df_train['contaminated']

# Train only on normal data (unsupervised anomaly detection)
X_normal = X[y == 0]

# Standardize features
scaler = StandardScaler()
X_normal_scaled = scaler.fit_transform(X_normal)

# Start MLflow run
with mlflow.start_run(run_name=f"contamination-detector-{datetime.now().strftime('%Y%m%d-%H%M%S')}") as run:

    # Model parameters
    contamination_rate = 0.05  # Expected contamination rate
    n_estimators = 100
    max_samples = 256
    random_state = 42

    # Log parameters
    mlflow.log_param("model_type", "IsolationForest")
    mlflow.log_param("contamination_rate", contamination_rate)
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_samples", max_samples)

    # Train model
    model = IsolationForest(
        contamination=contamination_rate,
        n_estimators=n_estimators,
        max_samples=max_samples,
        random_state=random_state,
        n_jobs=-1
    )

    model.fit(X_normal_scaled)

    # Evaluate on test set
    X_test_scaled = scaler.transform(X)
    predictions = model.predict(X_test_scaled)
    anomaly_scores = model.score_samples(X_test_scaled)

    # Convert predictions (-1 = anomaly, 1 = normal) to (1 = contaminated, 0 = normal)
    y_pred = np.where(predictions == -1, 1, 0)

    # Calculate metrics
    from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

    # Convert anomaly scores to probabilities (0-1 range)
    contamination_probs = 1 - (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min())

    precision = precision_score(y, y_pred)
    recall = recall_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    auc = roc_auc_score(y, contamination_probs)

    # Log metrics
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("auc_roc", auc)
    mlflow.log_metric("false_positive_rate", 1 - precision)

    print(f"Model Performance:")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    print(f"  F1 Score: {f1:.3f}")
    print(f"  AUC-ROC: {auc:.3f}")
    print(f"  False Positive Rate: {1-precision:.3f}")

    # Log model and scaler
    mlflow.sklearn.log_model(model, "model")
    mlflow.sklearn.log_model(scaler, "scaler")

    # Log feature importance (based on anomaly contribution)
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': np.abs(X_normal_scaled.std(axis=0))
    }).sort_values('importance', ascending=False)

    mlflow.log_dict(feature_importance.to_dict(), "feature_importance.json")

    # Register model
    model_uri = f"runs:/{run.info.run_id}/model"
    model_details = mlflow.register_model(model_uri, "contamination_detector")

    print(f"\nModel registered: {model_details.name} version {model_details.version}")
    print(f"Run ID: {run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Real-Time Inference

# COMMAND ----------

# Load latest model
model_name = "contamination_detector"
model_version = "latest"

loaded_model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")
loaded_scaler = mlflow.sklearn.load_model(f"models:/{model_name}/{model_version}")

# Test with new data
test_sample = pd.DataFrame({
    'ph_mean': [7.2],
    'ph_std': [0.15],
    'temp_mean': [37.0],
    'temp_std': [0.05],
    'do_mean': [38],
    'do_std': [5],
    'cell_density_growth_rate': [0.18],
    'glucose_consumption_rate': [0.65],
    'lactate_production_rate': [0.35]
})

# Predict
test_scaled = loaded_scaler.transform(test_sample)
prediction = loaded_model.predict(test_scaled)
risk_score = 1 - (loaded_model.score_samples(test_scaled)[0] - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min())

print(f"Contamination Risk Score: {risk_score:.3f}")
print(f"Prediction: {'CONTAMINATION DETECTED' if prediction[0] == -1 else 'Normal'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Monitoring & Retraining Schedule
# MAGIC
# MAGIC - **Inference Frequency**: Every 5 minutes for active bioreactors
# MAGIC - **Retraining**: Weekly with new data
# MAGIC - **Performance Monitoring**: Track false positive/negative rates
# MAGIC - **Alert Threshold**: Risk score > 0.75
