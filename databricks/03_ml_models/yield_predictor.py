"""
Batch Yield Prediction ML Model
Uses XGBoost to predict final batch yield based on early process parameters
MLflow tracking for model versioning
"""
# Databricks notebook source
# MAGIC %md
# MAGIC # Batch Yield Prediction Model
# MAGIC
# MAGIC **Model Type**: XGBoost Regressor
# MAGIC
# MAGIC **Purpose**: Predict final batch yield using first 24-48 hours of process data
# MAGIC
# MAGIC **Features**:
# MAGIC - Early cell density growth patterns
# MAGIC - Glucose consumption rates
# MAGIC - Lactate production rates
# MAGIC - Temperature and pH stability
# MAGIC - Raw material lot attributes
# MAGIC
# MAGIC **Performance Target**: R² > 0.90, RMSE < 3%

# COMMAND ----------

import mlflow
import mlflow.xgboost
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pandas as pd
import numpy as np
from datetime import datetime

mlflow.set_experiment("/Pharma-Digital-Twin/Yield-Prediction")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Training Data

# COMMAND ----------

def generate_yield_training_data(n_batches=1000):
    """Generate synthetic batch yield data"""

    np.random.seed(42)

    # Features from first 24-48 hours
    data = {
        # Early process parameters
        'cell_density_24h': np.random.normal(0.5, 0.1, n_batches),
        'cell_density_48h': np.random.normal(1.2, 0.2, n_batches),
        'viability_24h': np.random.normal(97, 2, n_batches),
        'viability_48h': np.random.normal(96, 2.5, n_batches),

        # Metabolite rates
        'glucose_consumption_rate': np.random.normal(0.5, 0.15, n_batches),
        'lactate_production_rate': np.random.normal(0.2, 0.08, n_batches),

        # Process stability
        'temp_variance_24h': np.random.uniform(0.01, 0.15, n_batches),
        'ph_variance_24h': np.random.uniform(0.01, 0.1, n_batches),

        # Raw material quality
        'media_lot_quality_score': np.random.normal(95, 5, n_batches),
        'cell_line_passage_number': np.random.randint(5, 25, n_batches),

        # Environmental
        'inoculation_density': np.random.normal(0.3, 0.05, n_batches),
    }

    df = pd.DataFrame(data)

    # Calculate yield based on features (realistic relationship)
    base_yield = 90

    # Positive factors
    yield_variation = (
        (df['cell_density_48h'] - 1.2) * 10 +  # Higher early density = better yield
        (df['viability_48h'] - 96) * 0.5 +  # Higher viability = better yield
        (df['media_lot_quality_score'] - 95) * 0.3 +  # Better media = better yield
        -(df['lactate_production_rate'] - 0.2) * 15  # Lower lactate = better yield
    )

    # Negative factors (stability issues)
    stability_penalty = (
        -df['temp_variance_24h'] * 20 +
        -df['ph_variance_24h'] * 15 +
        -(df['cell_line_passage_number'] - 15) * 0.1  # Higher passages = slight decline
    )

    # Final yield with noise
    df['yield_percent'] = base_yield + yield_variation + stability_penalty + np.random.normal(0, 2, n_batches)

    # Clamp to realistic range
    df['yield_percent'] = df['yield_percent'].clip(75, 98)

    return df

# Generate training data
df_train = generate_yield_training_data(n_batches=1000)
print(f"Training data shape: {df_train.shape}")
print(f"Average yield: {df_train['yield_percent'].mean():.1f}%")
print(f"Yield range: {df_train['yield_percent'].min():.1f}% - {df_train['yield_percent'].max():.1f}%")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train XGBoost Model

# COMMAND ----------

# Prepare data
feature_cols = [col for col in df_train.columns if col != 'yield_percent']
X = df_train[feature_cols]
y = df_train['yield_percent']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train with MLflow
with mlflow.start_run(run_name=f"yield-predictor-{datetime.now().strftime('%Y%m%d-%H%M%S')}") as run:

    # Model parameters
    params = {
        'n_estimators': 200,
        'max_depth': 6,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'objective': 'reg:squarederror'
    }

    # Log parameters
    mlflow.log_params(params)

    # Train model
    model = XGBRegressor(**params)
    model.fit(X_train, y_train)

    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Calculate metrics
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)

    # Log metrics
    mlflow.log_metric("train_rmse", train_rmse)
    mlflow.log_metric("test_rmse", test_rmse)
    mlflow.log_metric("train_r2", train_r2)
    mlflow.log_metric("test_r2", test_r2)
    mlflow.log_metric("test_mae", test_mae)

    print(f"Model Performance:")
    print(f"  Train RMSE: {train_rmse:.2f}%")
    print(f"  Test RMSE: {test_rmse:.2f}%")
    print(f"  Train R²: {train_r2:.3f}")
    print(f"  Test R²: {test_r2:.3f}")
    print(f"  Test MAE: {test_mae:.2f}%")

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\nTop 5 Features:")
    print(feature_importance.head())

    # Log model
    mlflow.xgboost.log_model(model, "model")
    mlflow.log_dict(feature_importance.to_dict(), "feature_importance.json")

    # Register model
    model_uri = f"runs:/{run.info.run_id}/model"
    model_details = mlflow.register_model(model_uri, "yield_predictor")

    print(f"\nModel registered: {model_details.name} version {model_details.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Inference

# COMMAND ----------

# Load model
model_name = "yield_predictor"
loaded_model = mlflow.xgboost.load_model(f"models:/{model_name}/latest")

# Test prediction
test_batch = pd.DataFrame({
    'cell_density_24h': [0.55],
    'cell_density_48h': [1.35],
    'viability_24h': [98],
    'viability_48h': [97],
    'glucose_consumption_rate': [0.48],
    'lactate_production_rate': [0.18],
    'temp_variance_24h': [0.03],
    'ph_variance_24h': [0.02],
    'media_lot_quality_score': [97],
    'cell_line_passage_number': [12],
    'inoculation_density': [0.32]
})

predicted_yield = loaded_model.predict(test_batch)[0]
print(f"Predicted Yield: {predicted_yield:.1f}%")

# Confidence interval (based on model uncertainty)
prediction_std = test_rmse
confidence_low = predicted_yield - 1.96 * prediction_std
confidence_high = predicted_yield + 1.96 * prediction_std

print(f"95% Confidence Interval: [{confidence_low:.1f}%, {confidence_high:.1f}%]")
