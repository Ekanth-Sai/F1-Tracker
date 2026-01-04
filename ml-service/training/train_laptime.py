"""
This script trains a machine learning regression model to predict
the next lap time of an F1 driver based on race and car conditions.

Purpose:
- Generate synthetic lap-time training data
- Train a RandomForest regressor
- Evaluate model performance
- Save the trained model for use in the ML prediction service

This script is intended to be run offline (not as an API).
"""

import numpy as np 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib 
from pathlib import Path 

def generate_synthetic_laptime_data(n_samples = 5000):
    np.random.seed(42)
    
    data = []
    lap_times = []
    
    for _ in range(n_samples):
        lap = np.random.randint(1, 60)
        tyre_age = np.random.randint(0, 40)
        tyre_compound = np.random.randint(0, 3)
        fuel_load = np.random.uniform(20, 100)
        track_temp = np.random.uniform(25, 50)
        avg_recent = np.random.uniform(85, 95)
        trend = np.random.uniform(-2, 2)
        speed = np.random.uniform(280, 320)
        
        base_time = 88.0
        tyre_deg = tyre_age * 0.05 if tyre_compound == 0 else tyre_age * 0.03
        fuel_effect = (fuel_load - 50) * 0.02
        temp_effect = (track_temp - 35) * 0.05
        
        lap_time = base_time + tyre_deg + fuel_effect + temp_effect + np.random.normal(0, 0.5)
        
        data.append([lap, tyre_age, tyre_compound, fuel_load, track_temp, avg_recent, trend, speed])
        lap_times.append(lap_time)
    
    return np.array(data), np.array(lap_times)

def train_laptime_model():
    print("Generating training data...")
    X, y = generate_synthetic_laptime_data()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    print("\nModel Performance:")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.3f} seconds")
    print(f"R² Score: {r2_score(y_test, y_pred):.3f}")
    
    # Save model
    model_dir = Path(__file__).parent.parent / "saved_models"
    model_dir.mkdir(exist_ok=True)
    joblib.dump(model, model_dir / "laptime_model.joblib")
    print(f"Model saved to {model_dir / 'laptime_model.joblib'}")

if __name__ == "__main__":
    train_laptime_model()