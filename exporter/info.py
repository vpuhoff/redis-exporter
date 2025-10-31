"""Parser for Redis INFO command output"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Regex patterns for parsing
RE_MASTER_HOST = re.compile(r"^master(_[0-9]+)?_host")
RE_MASTER_PORT = re.compile(r"^master(_[0-9]+)?_port")
RE_SLAVE = re.compile(r"^slave\d+")


def parse_db_keyspace_string(field_key: str, field_value: str) -> Optional[Tuple[int, int, int, int]]:
    """
    Parse keyspace info string
    
    Format: db0:keys=1,expires=0,avg_ttl=0
    
    Returns:
        Tuple (keys, keys_expiring, avg_ttl, keys_cached) or None
    """
    keys = 0
    keys_expiring = 0
    avg_ttl = -1
    keys_cached = -1
    
    for item in field_value.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        try:
            val = int(value)
        except (ValueError, TypeError):
            continue
        
        if key == "keys":
            keys = val
        elif key == "expires":
            keys_expiring = val
        elif key == "avg_ttl":
            avg_ttl = val
        elif key == "keys_cached":
            keys_cached = val
    
    return (keys, keys_expiring, avg_ttl, keys_cached)


def parse_command_stats(field_key: str, field_value: str) -> Optional[Tuple[str, float, float, float, float, bool]]:
    """
    Parse command stats
    
    Format: cmdstat_get:calls=2,usec=10,usec_per_call=5.00
    Extended: cmdstat_get:calls=21,usec=175,usec_per_call=8.33,rejected_calls=0,failed_calls=0
    
    Returns:
        Tuple (cmd, calls, rejected_calls, failed_calls, usec_total, extended_stats) or None
    """
    if not field_key.startswith("cmdstat_"):
        return None
    
    cmd = field_key[8:]  # Remove "cmdstat_" prefix
    calls = 0.0
    rejected_calls = 0.0
    failed_calls = 0.0
    usec_total = 0.0
    extended_stats = False
    
    for item in field_value.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        try:
            val = float(value)
        except (ValueError, TypeError):
            continue
        
        if key == "calls":
            calls = val
        elif key == "usec":
            usec_total = val
        elif key == "rejected_calls":
            rejected_calls = val
            extended_stats = True
        elif key == "failed_calls":
            failed_calls = val
            extended_stats = True
    
    return (cmd, calls, rejected_calls, failed_calls, usec_total, extended_stats)


def parse_error_stats(field_key: str, field_value: str) -> Optional[Tuple[str, float]]:
    """
    Parse error stats
    
    Format: errorstat_ERR:count=4
    
    Returns:
        Tuple (error_type, count) or None
    """
    if not field_key.startswith("errorstat_"):
        return None
    
    error_type = field_key[10:]  # Remove "errorstat_" prefix
    count = 0.0
    
    if field_value.startswith("count="):
        try:
            count = float(field_value[6:])  # Remove "count=" prefix
        except (ValueError, TypeError):
            return None
    
    return (error_type, count)


def extract_info_metrics(
    info_string: str,
    metric_map_gauges: Dict[str, str],
    metric_map_counters: Dict[str, str],
    collector: object,
) -> str:
    """
    Extract metrics from Redis INFO command output
    
    Args:
        info_string: Redis INFO output
        metric_map_gauges: Map of gauge metrics
        metric_map_counters: Map of counter metrics
        collector: RedisExporter collector instance
    
    Returns:
        Instance role (master/slave)
    """
    lines = info_string.split("\n")
    field_class = ""
    key_values = {}
    handled_dbs = {}
    cmd_stats = []
    error_stats = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Section header
        if line.startswith("# "):
            field_class = line[2:]
            continue
        
        # Parse field
        if ":" not in line or len(line) < 2:
            continue
        
        split = line.split(":", 1)
        field_key = split[0]
        field_value = split[1] if len(split) > 1 else ""
        
        key_values[field_key] = field_value
        
        # Handle different sections
        if field_class == "Keyspace" or field_key.startswith("db"):
            result = parse_db_keyspace_string(field_key, field_value)
            if result:
                keys, keys_expiring, avg_ttl, keys_cached = result
                collector._register_metric("db_keys", keys, labels={"db": field_key})
                collector._register_metric("db_keys_expiring", keys_expiring, labels={"db": field_key})
                if keys_cached > -1:
                    collector._register_metric("db_keys_cached", keys_cached, labels={"db": field_key})
                if avg_ttl > -1:
                    collector._register_metric("db_avg_ttl_seconds", avg_ttl, labels={"db": field_key})
                handled_dbs[field_key] = True
                continue
        
        elif field_class == "Commandstats":
            result = parse_command_stats(field_key, field_value)
            if result:
                cmd_stats.append(result)
                continue
        
        elif field_class == "Errorstats":
            result = parse_error_stats(field_key, field_value)
            if result:
                error_stats.append(result)
                continue
        
        # Check if metric should be included
        if not _should_include_metric(field_key, metric_map_gauges, metric_map_counters):
            continue
        
        # Parse and register metric
        metric_name = _get_metric_name(field_key, metric_map_gauges, metric_map_counters)
        value = _parse_metric_value(field_value)
        
        if value is not None:
            # Handle special case
            if metric_name == "latest_fork_usec":
                metric_name = "latest_fork_seconds"
                value = value / 1e6
            
            # Determine if counter or gauge
            is_counter = field_key in metric_map_counters
            
            collector._create_metric_descr(metric_name)
            collector._register_metric(metric_name, value, is_counter=is_counter)
    
    # Register command stats
    for cmd, calls, rejected_calls, failed_calls, usec_total, extended in cmd_stats:
        collector._create_metric_descr("commands_total", labels=["cmd"])
        collector._create_metric_descr("commands_duration_seconds_total", labels=["cmd"])
        collector._register_metric("commands_total", calls, is_counter=True, labels={"cmd": cmd})
        collector._register_metric("commands_duration_seconds_total", usec_total / 1e6, 
                       is_counter=True, labels={"cmd": cmd})
        
        if extended:
            collector._create_metric_descr("commands_rejected_calls_total", labels=["cmd"])
            collector._create_metric_descr("commands_failed_calls_total", labels=["cmd"])
            collector._register_metric("commands_rejected_calls_total", rejected_calls,
                           is_counter=True, labels={"cmd": cmd})
            collector._register_metric("commands_failed_calls_total", failed_calls,
                           is_counter=True, labels={"cmd": cmd})
    
    # Register error stats
    for error_type, count in error_stats:
        collector._create_metric_descr("errors_total", labels=["err"])
        collector._register_metric("errors_total", count, is_counter=True, labels={"err": error_type})
    
    # Register instance info
    instance_role = key_values.get("role", "")
    instance_labels = {
        "role": instance_role,
        "redis_version": key_values.get("redis_version", ""),
        "redis_build_id": key_values.get("redis_build_id", ""),
        "redis_mode": key_values.get("redis_mode", ""),
        "os": key_values.get("os", ""),
        "maxmemory_policy": key_values.get("maxmemory_policy", ""),
        "tcp_port": key_values.get("tcp_port", ""),
        "run_id": key_values.get("run_id", ""),
        "process_id": key_values.get("process_id", ""),
        "master_replid": key_values.get("master_replid", ""),
    }
    
    collector._create_metric_descr("instance_info", labels=list(instance_labels.keys()))
    collector._register_metric("instance_info", 1.0, labels=instance_labels)
    
    return instance_role


def _should_include_metric(field_key: str, metric_map_gauges: Dict[str, str], 
                          metric_map_counters: Dict[str, str]) -> bool:
    """Check if metric should be included"""
    if field_key.startswith("db") or field_key.startswith("cmdstat_"):
        return True
    return field_key in metric_map_gauges or field_key in metric_map_counters


def _get_metric_name(field_key: str, metric_map_gauges: Dict[str, str],
                    metric_map_counters: Dict[str, str]) -> str:
    """Get metric name from field key"""
    if field_key in metric_map_gauges:
        return metric_map_gauges[field_key]
    if field_key in metric_map_counters:
        return metric_map_counters[field_key]
    # Sanitize and return as-is
    from .metrics import sanitize_metric_name
    return sanitize_metric_name(field_key)


def _parse_metric_value(field_value: str) -> Optional[float]:
    """Parse metric value"""
    from .metrics import parse_metric_value
    return parse_metric_value(field_value)

