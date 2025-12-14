from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os

from app.utils.llm import llm_bangla_explain
from app.utils.bangla_voice import tts_to_mp3_bytes

router = APIRouter()

TREATMENTS_PATH = os.path.join("app", "models", "disease_treatments.json")
with open(TREATMENTS_PATH, "r", encoding="utf-8") as f:
    TREATMENTS = json.load(f)

class RecommendRequest(BaseModel):
    disease_label: str
    confidence: float
    health_score: float
    yellowing_pct: float
    spots_pct: float
    weather: Optional[Dict[str, Any]] = None
    soil: Optional[Dict[str, Any]] = None

class RecommendResponse(BaseModel):
    advice_bn: str
    audio_mp3_base64: str

import base64

def _status_from_score(score: float) -> str:
    if score >= 80: return "healthy"
    if score >= 55: return "warning"
    return "critical"

@router.post("/get-recommendation", response_model=RecommendResponse)
def get_recommendation(req: RecommendRequest):
    label = req.disease_label
    mapping = TREATMENTS.get(label, TREATMENTS.get("_default"))

    # Weather summary
    rain_mm_48h = None
    max_temp = None
    if req.weather:
        rain_mm_48h = req.weather.get("rain_mm_48h")
        max_temp = req.weather.get("max_temp_c")

    # Soil summary
    soil_tex = None
    ph = None
    if req.soil:
        soil_tex = req.soil.get("texture_class_bn")
        ph = req.soil.get("ph")

    status = _status_from_score(req.health_score)

    # --- Rule-based recommendations (Bangla) ---
    lines = []
    lines.append(f"আপনার ফসলের স্বাস্থ্য স্কোর প্রায় {int(round(req.health_score))}% ({'ভালো' if status=='healthy' else 'সতর্কতা' if status=='warning' else 'ঝুঁকিপূর্ণ'} অবস্থা)।")

    # Disease
    disease_bn = mapping.get("disease_bn", "রোগ")
    crop_bn = mapping.get("crop", "ফসল")
    lines.append(f"সম্ভাব্য রোগ: {crop_bn} — {disease_bn} (বিশ্বাসযোগ্যতা {int(req.confidence*100)}%)।")

    # Actions
    actions = mapping.get("actions_bn", [])
    if actions:
        lines.append("প্রাথমিক করণীয়:")
        for a in actions[:4]:
            lines.append(f"• {a}")

    # Irrigation advice based on rain
    if rain_mm_48h is not None:
        if rain_mm_48h >= 15:
            lines.append(f"আগামী ২ দিনে প্রায় {rain_mm_48h:.0f} মিমি বৃষ্টির সম্ভাবনা আছে—আজ ভারী সেচ না দিলেই ভালো।")
        elif rain_mm_48h >= 5:
            lines.append(f"আগামী ২ দিনে প্রায় {rain_mm_48h:.0f} মিমি বৃষ্টি হতে পারে—মাটি আর্দ্রতা দেখে হালকা সেচ দিন।")
        else:
            lines.append(f"আগামী ২ দিনে বৃষ্টি কম (≈{rain_mm_48h:.0f} মিমি)—আজ মাটি শুকনো হলে সেচ দিন।")

    # Heat stress
    if max_temp is not None and max_temp >= 34:
        lines.append(f"তাপমাত্রা বেশি থাকতে পারে (সর্বোচ্চ ≈{max_temp:.0f}°C)—সকাল/বিকেলে সেচ দিন, দুপুরে নয়।")

    # Fertilizer hint from yellowing
    if req.yellowing_pct >= 15:
        lines.append("পাতা হলদে বেশি—নাইট্রোজেন ঘাটতি হতে পারে। ইউরিয়া/কম্পোস্ট স্থানীয় পরামর্শ অনুযায়ী দিন।")

    # Spots hint
    if req.spots_pct >= 8:
        lines.append("পাতায় দাগ/স্পট তুলনামূলক বেশি—পাতা ভেজা রাখা কমান এবং আক্রান্ত পাতাগুলো সরান।")

    # Soil
    if soil_tex:
        lines.append(f"মাটির ধরন: {soil_tex}।")
    if ph is not None:
        lines.append(f"মাটির pH আনুমানিক {ph:.1f}।")

    rules_bn = "\n".join(lines)

    # Optional LLM polishing
    context = {
        "disease_label": label,
        "health_score": req.health_score,
        "yellowing_pct": req.yellowing_pct,
        "spots_pct": req.spots_pct,
        "weather": req.weather,
        "soil": req.soil
    }
    advice_bn = llm_bangla_explain(rules_bn, context)

    # TTS
    mp3_bytes = tts_to_mp3_bytes(advice_bn, lang="bn")
    audio_b64 = base64.b64encode(mp3_bytes).decode("utf-8")

    return RecommendResponse(advice_bn=advice_bn, audio_mp3_base64=audio_b64)
