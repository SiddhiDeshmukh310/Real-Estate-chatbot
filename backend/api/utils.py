"""
Utilities, UTF-8 clean string formatting, caching, and logging for Real Estate Insights.
"""

import logging
import math
from typing import Dict, Any
import numpy as np

logger = logging.getLogger("real_estate_insights")

# Global in-memory cache for repeated queries
_QUERY_CACHE: Dict[str, Dict[str, Any]] = {}


def cache_get(query_key: str) -> Dict[str, Any]:
    return _QUERY_CACHE.get(query_key)


def cache_set(query_key: str, response_data: Dict[str, Any]) -> None:
    if len(_QUERY_CACHE) > 200:
        _QUERY_CACHE.clear()
    _QUERY_CACHE[query_key] = response_data


def make_json_safe(obj: Any) -> Any:
    """Recursively convert NaN/inf and numpy scalar types to JSON-safe Python types."""
    if isinstance(obj, np.generic):
        obj = obj.item()

    if obj is None or isinstance(obj, (str, bool, int)):
        return obj

    if isinstance(obj, float):
        if not math.isfinite(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [make_json_safe(v) for v in obj]

    return str(obj)

