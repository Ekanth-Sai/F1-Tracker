"""
This FastAPI application exposes ML models uded by the F1 tracker backend for real-time predictions.

Responsibilities:
- Loads trained ML models at startup 
- Predict pit stop probability 
- Predict next lap time 
- Expose HTTP APIs for Spring Boot backend

This is a stateless service and can be deployed independently.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import joblib 
import numpy as np 
from pathlib import Path 
import logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title = "F1 ML Prediction Service", version = "1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

MODEL_DIR = Path(__file__).parent.parent / "saved_models"
pitstop_model = None
laptime_model = None 

@app.on_event("startup")
async def load_models():
    global pitstop_model, laptime_model 
    try:
        pitstop_model = joblib.load(MODEL_DIR / "pitstop_model.joblib")
        laptime_model = joblib.load(MODEL_DIR / "laptime_model.joblib")
        logger.info("Models loaded successfully")
    except FileNotFoundError:
        logger.warning("Models not found. Train models first.")

class PitStopRequest(BaseModel):
    driver_number: int
    current_lap: int
    tyre_age: int
    tyre_compound: int
    position: int 
    gap_to_leader: int 
    recent_lap_times: list[float]
    avg_speed: float 
    
class PitStopResponse(BaseModel):
    driver_number: int 
    pit_probability: float 
    confidence: float 
    recommendation: str
    
class LapTimeRequest(BaseModel):
    driver_number: int 
    current_lap: int 
    tyre_age: int 
    tyre_compound: int 
    fuel_load: float 
    track_temp: float 
    recent_lap_times: list[float]
    avg_speed: float 
    

class LapTimeResponse(BaseModel):
    driver_number: int 
    predicted_lap_time: float 
    confidence_interval: tuple[float, float]
    
def encode_tyre_compound(compound: str) -> int:
    mapping = {
        "SOFT": 0,
        "MEDIUM": 1,
        "HARD": 2,
        "INTERMEDIATE": 3,
        "WET": 4
    }
    
    return mapping.get(compound.upper(), 1) 

def prepare_pitstop_features(request: PitStopRequest) -> np.ndarray:
    avg_recent_lap = np.mean(request.recent_lap_times) if request.recent_lap_times else 90.0
    lap_variance = np.var(request.recent_lap_times) if len(request.recent_lap_times) > 1 else 0.0
    
    features = np.array([
        request.current_lap,
        request.tyre_age,
        encode_tyre_compound(request.tyre_compound),
        request.position,
        request.gap_to_leader,
        avg_recent_lap,
        lap_variance,
        request.avg_speed
    ]).reshape(1, -1)
    
    return features 

def prepare_laptime_features(request: LapTimeRequest) -> np.ndarray:
    avg_recent_lap = np.mean(request.recent_lap_times) if request.recent_lap_times else 90.0
    
    trend = 0.0
    
    if len(request.recent_lap_times) >= 2:
        trend = request.recent_lap_times[-1] - request.recent_lap_times[0]
        
    features = np.array([
        request.current_lap,
        request.tyre_age,
        encode_tyre_compound(request.tyre_compound),
        request.fuel_load,
        request.track_temp,
        avg_recent_lap,
        trend,
        request.avg_speed
    ]).reshape(1, -1)
    
    return features 

@app.get("/")
async def root():
    return {
        "service": "F1 ML Prediction Service",
        "version": "1.0.0",
        "endpoints": ["/predict/pitstop", "/predict/nextlap", "/health"]
    }
    
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": {
            "pitstop": pitstop_model is not None,
            "laptime": laptime_model is not None
        }
    }
    
@app.post("/predict/pitstop", response_model = PitStopResponse)
async def predict_pitstop(request: PitStopRequest):
    if pitstop_model is None:
        raise HTTPException(status_code = 503, detail = "Pit stop model not loaded.")
    
    try:
        features = prepare_pitstop_features(request)
        probability = pitstop_model.predict_proba(features)[0][1]
        
        if probability > 0.7:
            recommendation = "HIGH - Pit stop likely within 3 laps"
        elif probability > 0.4:
            recommendation = "MEDIUM - Monitor tyre degradation"
        else:
            recommendation = "LOW - Continue current stint"
            
        return PitStopResponse(
            driver_number = request.driver_number,
            pit_probability = round(float(probability), 3),
            confidence = round(float(max(probability, 1 - probability)), 3),
            recommendation = recommendation
        )
        
    except Exception as e:
        logger.error(f"Pit stop prediction error: {str(e)}")
        raise HTTPException(status_code = 500, detail = f"Prediction failed: {str(e)}")

@app.post("/predict/nextlap", response_model = LapTimeResponse)
async def predict_next_lap(request: LapTimeRequest):
    if laptime_model is None:
        raise HTTPException(status_code = 503, detail = "Lap time model not loaded.")
    
    try:
        features = prepare_laptime_features(request)
        predicted_time = laptime_model.predict(features)[0]
        
        confidence_range = 0.5
        confidence_interval = (
            round(float(predicted_time - confidence_range), 3),
            round(float(predicted_time + confidence_range), 3)
        )
        
        return LapTimeResponse(
            driver_number = request.driver_number,
            predicted_lap_time = round(float(predicted_time), 3),
            confidence_interval = confidence_interval
        )
    except Exception as e:
        logger.error(f"Lap time prediction error: {str(e)}")
        raise HTTPException(status_code = 500, detail = f"Prediction failed: {str(e)}")