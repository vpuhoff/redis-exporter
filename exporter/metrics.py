"""Helper functions for metric registration"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Regex for sanitizing metric names
_METRIC_NAME_RE = re.compile(r"[^a-zA-Z0-9_]")


def sanitize_metric_name(name: str) -> str:
    """Sanitize metric name by replacing invalid characters with underscores"""
    return _METRIC_NAME_RE.sub("_", name)


def parse_metric_value(value: str) -> Optional[float]:
    """
    Parse metric value from string
    
    Handles boolean values and numeric values
    
    Returns:
        Float value or None if parsing failed
    """
    if value is None:
        return None
    
    value_lower = value.lower()
    
    if value_lower in ("ok", "true"):
        return 1.0
    if value_lower in ("err", "fail", "false"):
        return 0.0
    
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.debug(f"Couldn't parse metric value: {value}")
        return None


def format_keyspace_info(db_name: str, info: str) -> List[Tuple[str, float, Dict[str, str]]]:
    """
    Parse keyspace info and return list of (metric_name, value, labels)
    
    Format: db0:keys=1,expires=0,avg_ttl=0
    
    Returns:
        List of tuples: (metric_name, value, labels_dict)
    """
    results = []
    for item in info.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            continue
        
        metric_name = f"keyspace_{key}"
        labels = {"db": db_name}
        results.append((metric_name, value_float, labels))
    
    return results


def format_cmdstat_info(cmd_name: str, info: str) -> List[Tuple[str, float, Dict[str, str]]]:
    """
    Parse cmdstat info and return list of metrics
    
    Format: cmdstat_get:calls=2,usec=10,usec_per_call=5.00
    
    Returns:
        List of tuples: (metric_name, value, labels_dict)
    """
    results = []
    for item in info.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            continue
        
        # Convert to snake_case
        metric_key = key.replace("usec_per_call", "per_call")
        metric_name = sanitize_metric_name(f"command_{cmd_name}_{metric_key}")
        labels = {"cmd": cmd_name}
        results.append((metric_name, value_float, labels))
    
    return results


def format_latest_fork_usec(value: float) -> float:
    """Convert microseconds to seconds"""
    return value / 1e6


def should_include_metric(field_key: str, metric_map_gauges: Dict[str, str], 
                          metric_map_counters: Dict[str, str]) -> bool:
    """
    Check if metric should be included in export
    
    Args:
        field_key: Field key from Redis INFO
        metric_map_gauges: Map of gauge metrics
        metric_map_counters: Map of counter metrics
    
    Returns:
        True if metric should be included
    """
    # Always include db* keys
    if field_key.startswith("db"):
        return True
    
    # Include cmdstat_* metrics
    if field_key.startswith("cmdstat_"):
        return True
    
    # Check if in metric maps
    if field_key in metric_map_gauges or field_key in metric_map_counters:
        return True
    
    return False

