from typing import Dict, Any, List
import time

RECENT_RESULTS: List[Dict[str, Any]] = []

def save_recent_result(result: Dict[str, Any], limit: int = 20):
    result2 = dict(result)
    result2["ts"] = int(time.time())
    RECENT_RESULTS.insert(0, result2)
    del RECENT_RESULTS[limit:]

def get_recent_results() -> List[Dict[str, Any]]:
    return RECENT_RESULTS
