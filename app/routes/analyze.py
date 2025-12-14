from fastapi import APIRouter, UploadFile, File
from typing import Optional
from PIL import Image
import io
import numpy as np
import cv2
import os

from app.models.disease_model import PlantVillageModel
from app.utils.health_score import compute_leaf_health_metrics, compute_health_score
from app.utils.weather import get_weather_summary
from app.utils.soil import get_soil_summary
from app.utils.storage import save_recent_result

router = APIRouter()

# Choose a PlantVillage model on Hugging Face
MODEL_ID = os.getenv("PLANTVILLAGE_MODEL_ID", "Akshay0706/Plant-Village-1-Epochs-Model")
model = PlantVillageModel(MODEL_ID)

@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    lat: Optional[float] = None,
    lon: Optional[float] = None
):
    # Read image
    data = await image.read()
    pil = Image.open(io.BytesIO(data)).convert("RGB")

    # Disease prediction
    pred = model.predict(pil)

    # Health score via OpenCV
    rgb = np.array(pil)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    metrics = compute_leaf_health_metrics(bgr)

    # Weather & soil (optional lat/lon)
    weather = get_weather_summary(lat, lon) if lat is not None and lon is not None else None
    soil = get_soil_summary(lat, lon) if lat is not None and lon is not None else None

    heat_stress_pct = 0.0
    if weather and weather.get("max_temp_c") is not None:
        # simple heat stress heuristic
        t = weather["max_temp_c"]
        heat_stress_pct = max(0.0, min(100.0, (t - 30.0) * 10.0))  # 30C->0, 40C->100

    health, parts = compute_health_score(
        yellowing_pct=metrics["yellowing_pct"],
        spots_pct=metrics["spots_pct"],
        heat_stress_pct=heat_stress_pct
    )

    result = {
        "disease_label": pred.label,
        "confidence": pred.confidence,
        "health_score": health,
        "yellowing_pct": metrics["yellowing_pct"],
        "spots_pct": metrics["spots_pct"],
        "heat_stress_pct": heat_stress_pct,
        "weather": weather,
        "soil": soil
    }

    # Save for dashboard demo
    save_recent_result(result)

    return result
