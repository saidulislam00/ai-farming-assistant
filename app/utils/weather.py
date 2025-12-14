from typing import Optional, Dict, Any
import requests

def get_weather_summary(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Uses Open-Meteo daily forecast (no API key).
    Returns rain over next 48h and max temp (approx).
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "rain_sum,temperature_2m_max",
        "forecast_days": 2,
        "timezone": "auto"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        j = r.json()
        rain = j["daily"]["rain_sum"]
        tmax = j["daily"]["temperature_2m_max"]
        return {
            "rain_mm_48h": float(sum(rain)),
            "max_temp_c": float(max(tmax)) if tmax else None
        }
    except Exception:
        return None
