from fastapi import APIRouter
from typing import List, Dict, Any
import random

from app.utils.storage import get_recent_results

router = APIRouter()

def _status(score: float) -> str:
    if score >= 80: return "healthy"
    if score >= 55: return "warning"
    return "critical"

@router.get("/dashboard-data")
def dashboard_data() -> Dict[str, Any]:
    # Demo farms (static)
    farms = [
        {"farm_id": "F-101", "farmer": "রহিম", "crop": "টমেটো", "lat": 23.78, "lon": 90.41},
        {"farm_id": "F-102", "farmer": "করিম", "crop": "আলু", "lat": 24.37, "lon": 88.60},
        {"farm_id": "F-103", "farmer": "সুমি", "crop": "মরিচ", "lat": 22.36, "lon": 91.82},
        {"farm_id": "F-104", "farmer": "হাসান", "crop": "ধান", "lat": 24.90, "lon": 91.87},
        {"farm_id": "F-105", "farmer": "নূর", "crop": "বেগুন", "lat": 23.46, "lon": 91.18},
        {"farm_id": "F-106", "farmer": "মিনা", "crop": "টমেটো", "lat": 23.20, "lon": 90.00},
        {"farm_id": "F-107", "farmer": "সাদেক", "crop": "আলু", "lat": 25.62, "lon": 88.65}
    ]

    # Use recent analyzed results if available; otherwise synthesize demo scores
    recent = get_recent_results()
    for i, f in enumerate(farms):
        if i < len(recent):
            f["health_score"] = round(float(recent[i]["health_score"]), 1)
            f["disease_label"] = recent[i]["disease_label"]
        else:
            score = random.choice([92, 84, 76, 63, 51, 39])
            f["health_score"] = float(score)
            f["disease_label"] = random.choice(["healthy", "leaf_spot", "blight", "mosaic"])
        f["status"] = _status(f["health_score"])

    # Aggregation for chart
    counts = {"healthy": 0, "warning": 0, "critical": 0}
    for f in farms:
        counts[f["status"]] += 1

    return {"farms": farms, "counts": counts}
