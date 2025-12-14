from typing import Dict, Any, Tuple
import cv2
import numpy as np

def _percent(mask: np.ndarray) -> float:
    total = mask.size
    on = int(np.count_nonzero(mask))
    return (on / total) * 100.0 if total > 0 else 0.0

def compute_leaf_health_metrics(bgr_img: np.ndarray) -> Dict[str, Any]:
    """
    Input: BGR image (OpenCV)
    Returns: yellowing%, brown_spots%, plus debug masks if needed
    """
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # Rough yellow mask in HSV:
    # Hue around yellow-green; tune for your dataset.
    lower_yellow = np.array([15, 40, 40])
    upper_yellow = np.array([40, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Brown spots: lower saturation + darker value regions (very heuristic)
    lower_brown = np.array([5, 30, 20])
    upper_brown = np.array([25, 255, 160])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)

    # Cleanup masks
    kernel = np.ones((5, 5), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    brown_mask  = cv2.morphologyEx(brown_mask,  cv2.MORPH_OPEN, kernel, iterations=1)

    yellowing_pct = _percent(yellow_mask)
    spots_pct = _percent(brown_mask)

    return {
        "yellowing_pct": float(yellowing_pct),
        "spots_pct": float(spots_pct),
    }

def compute_health_score(
    yellowing_pct: float,
    spots_pct: float,
    heat_stress_pct: float
) -> Tuple[float, Dict[str, float]]:
    """
    Health = 100 - (yellowing*0.4) - (spots*0.4) - (heatStress*0.2)
    Clamp to 0..100
    """
    health = 100.0 - (yellowing_pct * 0.4) - (spots_pct * 0.4) - (heat_stress_pct * 0.2)
    health = max(0.0, min(100.0, health))

    return health, {
        "yellowing_weighted": yellowing_pct * 0.4,
        "spots_weighted": spots_pct * 0.4,
        "heat_weighted": heat_stress_pct * 0.2
    }
