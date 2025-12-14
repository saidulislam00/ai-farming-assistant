from typing import Optional, Dict, Any
import requests

def _texture_bn(sand: float, clay: float) -> str:
    # very rough texture classification (demo)
    if clay >= 40: return "কাদামাটি (Clay)"
    if sand >= 70: return "বালুমাটি (Sandy)"
    if clay >= 27 and sand <= 45: return "দোআঁশ/কাদাযুক্ত (Loam/Clay loam)"
    return "দোআঁশ (Loam)"

def get_soil_summary(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    SoilGrids point query. We fetch a few layers:
    - sand, clay (topsoil)
    - pH
    """
    try:
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        params = {
            "lat": lat,
            "lon": lon,
            "property": ["sand", "clay", "phh2o"],
            "depth": "0-5cm",
            "value": "mean"
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        j = r.json()

        props = {p["name"]: p for p in j.get("properties", [])}

        sand = props["sand"]["depths"][0]["values"]["mean"]
        clay = props["clay"]["depths"][0]["values"]["mean"]
        ph = props["phh2o"]["depths"][0]["values"]["mean"]

        tex_bn = _texture_bn(sand, clay)
        return {
            "sand": float(sand),
            "clay": float(clay),
            "ph": float(ph),
            "texture_class_bn": tex_bn
        }
    except Exception:
        return None
