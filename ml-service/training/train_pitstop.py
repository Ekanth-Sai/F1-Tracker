"""
This script trains a ML model that predicts whether an F1 driver is liely to make a pit stop in the near future. 

Purpose:
- Generate synthetic training data for pit stop scenarios 
- Train a RandomForest classifier 
- Evaluate model performance
- Save the trained model for use in the ML prediction service

This script is intended to be run offline and not as an API service.
"""

import numpy as np 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import classification_report, roc_auc_score 
import joblib 
from pathlib import Path 

def generate_synthetic_training_data(n_samples = 5000):
    """
    Features:
    - current lap
    - tyre age
    - tyre compound (0=SOFT, 1=MEDIUM, 2=HARD)
    - race position
    - gap to leader (seconds)
    - average recent lap time
    - lap time variance
    - average speed

    Label:
    - 1 = pit stop likely
    - 0 = continue current stint
    """
    
    np.random.seed(42)
    
    data = []
    labels = []
    
    for _ in range(n_samples):
        lap = np.random.randint(1, 60)
        tyre_age = np.random.randint(0, 40)
        tyre_compound = np.random.randint(0, 3)
        position = np.random.randint(1, 21)
        gap = np.random.uniform(0, 60)
        avg_lap = np.random.uniform(85, 95)
        variance = np.random.uniform(0, 2)
        speed = np.random.uniform(280, 320)
        
        pit = 1 if (tyre_age > 25 or (tyre_age > 15 and tyre_compound == 0)) else 0 
        
        if np.random.random() < 0.15:
            pit = 1 - pit 
        
        data.append([lap, tyre_age, tyre_compound, position, gap, avg_lap, variance, speed])
        labels.append(pit)
    
    return np.array(data), np.array(labels) 

def train_pitstop_model():
    print("Generating training data...")
    X, y = generate_synthetic_training_data() 
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    
    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    model = RandomForestClassifier(
        n_estimators = 100, 
        max_depth = 10, 
        min_samples_split = 20, 
        random_state = 42, 
        n_jobs = -1)
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print("\nModel performance: ")
    print(classification_report(y_test, y_pred))
    print(f"ROC AUC score: {roc_auc_score(y_test, y_proba):.3f}")
    
    model_dir = Path(__file__).parent.parent / "saved_models"
    model_dir.mkdir(exist_ok = True)
    joblib.dump(model, model_dir / "pitstop_model.joblib")
    print(f"Model saved to {model_dir / 'pitstop_model.joblib'}")

if __name__ == "__main__":
    train_pitstop_model() 
    
