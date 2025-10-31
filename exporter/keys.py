"""Key checking and scanning module"""

import logging
import re
from typing import List, Optional, Tuple
from urllib.parse import unquote

import redis

logger = logging.getLogger(__name__)

# Glob pattern detection
_GLOB_PATTERN = re.compile(r"[\?\*\[\]\^]+")


class DbKeyPair:
    """Database and key pair"""
    def __init__(self, db: str, key: str):
        self.db = db
        self.key = key


def parse_key_arg(keys_arg_string: str) -> List[DbKeyPair]:
    """
    Parse key arguments string
    
    Format: "db0=key1,db1=key2" or "key1,key2" (defaults to db0)
    
    Returns:
        List of DbKeyPair objects
    """
    if not keys_arg_string:
        logger.debug("Got empty key arguments, parsing skipped")
        return []
    
    keys = []
    for k in keys_arg_string.split(","):
        k = k.strip()
        if not k:
            continue
        
        parts = k.split("=", 1)
        
        if len(parts) == 1:
            # No db specified, default to db0
            db = "0"
            try:
                key = unquote(parts[0].strip())
            except Exception as e:
                logger.error(f"Couldn't parse db/key string: {k}, error: {e}")
                continue
        elif len(parts) == 2:
            # db=key format
            db_raw = parts[0].strip().replace("db", "")
            try:
                key = unquote(parts[1].strip())
            except Exception as e:
                logger.error(f"Couldn't parse db/key string: {k}, error: {e}")
                continue
            db = db_raw
        else:
            logger.error(f"Invalid key list argument: {k}")
            continue
        
        # Validate empty values
        if not db or not key:
            logger.error(f"Empty value parsed in pair db={db}, key={key}, skipping")
            continue
        
        # Validate db is a valid number
        try:
            db_num = int(db)
            if db_num < 0:
                logger.error(f"Invalid database index: {db}")
                continue
        except ValueError:
            logger.error(f"Invalid database index: {db}")
            continue
        
        keys.append(DbKeyPair(db, key))
    
    return keys


def scan_keys(client: redis.Redis, pattern: str, count: int = 100) -> List[bytes]:
    """
    Scan Redis for keys matching pattern
    
    Uses SCAN command which is safer than KEYS for production
    
    Returns:
        List of matching keys
    """
    if not pattern:
        raise ValueError("pattern shouldn't be empty")
    
    keys = []
    cursor = 0
    
    while True:
        cursor, batch = client.scan(cursor, match=pattern, count=count)
        keys.extend(batch)
        
        if cursor == 0:
            break
    
    return keys


def get_keys_from_patterns(client: redis.Redis, keys: List[DbKeyPair], count: int = 100) -> List[DbKeyPair]:
    """
    Expand key patterns using SCAN
    
    Returns:
        List of DbKeyPair objects with expanded keys
    """
    expanded_keys = []
    
    for k in keys:
        # Check if key contains glob pattern characters
        if _GLOB_PATTERN.search(k.key):
            # Need to SCAN for this pattern
            # Select database
            original_db = client.connection_pool.connection_kwargs.get('db', 0)
            try:
                if k.db != str(original_db):
                    client.execute_command("SELECT", int(k.db))
            except Exception as e:
                logger.error(f"Couldn't select database {k.db}: {e}")
                continue
            
            # Scan for keys
            try:
                scanned_keys = scan_keys(client, k.key, count)
                for key_name in scanned_keys:
                    expanded_keys.append(DbKeyPair(k.db, key_name.decode('utf-8') if isinstance(key_name, bytes) else key_name))
            except Exception as e:
                logger.error(f"Error with SCAN for pattern {k.key}: {e}")
                continue
            finally:
                # Restore original database
                if k.db != str(original_db):
                    client.execute_command("SELECT", original_db)
        else:
            # No pattern, just add as-is
            expanded_keys.append(k)
    
    return expanded_keys


def get_key_info(client: redis.Redis, key_name: str) -> Optional[Tuple[str, int, Optional[str]]]:
    """
    Get key type and size
    
    Returns:
        Tuple of (key_type, size, string_value) or None if error
    """
    try:
        key_type = client.type(key_name)
        if isinstance(key_type, bytes):
            key_type = key_type.decode('utf-8')
        
        if key_type == "none":
            logger.debug(f"Key '{key_name}' not found")
            return ("none", 0, None)
        
        size = 0
        str_val = None
        
        if key_type == "string":
            # Try to get string value
            try:
                str_val_bytes = client.get(key_name)
                if str_val_bytes:
                    if isinstance(str_val_bytes, bytes):
                        str_val = str_val_bytes.decode('utf-8')
                    else:
                        str_val = str(str_val_bytes)
                
                # Try PFCOUNT first for HyperLogLog
                try:
                    size = client.pfcount(key_name)
                except:
                    # Not HyperLogLog, try STRLEN
                    size = client.strlen(key_name)
                    
            except Exception as e:
                logger.error(f"Error getting string info for {key_name}: {e}")
                return None
                
        elif key_type == "list":
            size = client.llen(key_name)
        elif key_type == "set":
            size = client.scard(key_name)
        elif key_type == "zset":
            size = client.zcard(key_name)
        elif key_type == "hash":
            size = client.hlen(key_name)
        elif key_type == "stream":
            size = client.xlen(key_name)
        else:
            logger.error(f"Unknown key type: {key_type}")
            return None
        
        return (key_type, size, str_val)
        
    except Exception as e:
        logger.error(f"Error getting key info for {key_name}: {e}")
        return None


def extract_check_key_metrics(
    client: redis.Redis,
    check_keys: str,
    check_single_keys: str,
    collector: object,
) -> None:
    """
    Extract metrics for checked keys
    
    Args:
        client: Redis client
        check_keys: Comma-separated key patterns (uses SCAN)
        check_single_keys: Comma-separated specific keys (direct lookup)
        collector: RedisExporter collector instance
    """
    # Parse keys
    pattern_keys = parse_key_arg(check_keys)
    single_keys = parse_key_arg(check_single_keys)
    
    # Expand patterns if needed
    all_keys = single_keys.copy()
    if pattern_keys:
        try:
            expanded_keys = get_keys_from_patterns(client, pattern_keys)
            all_keys.extend(expanded_keys)
        except Exception as e:
            logger.error(f"Error expanding key patterns: {e}")
    
    logger.debug(f"Total keys to check: {len(all_keys)}")
    
    # Group keys by database for efficiency
    keys_by_db = {}
    for k in all_keys:
        if k.db not in keys_by_db:
            keys_by_db[k.db] = []
        keys_by_db[k.db].append(k.key)
    
    # Process each database
    original_db = client.connection_pool.connection_kwargs.get('db', 0)
    
    for db_num, key_list in keys_by_db.items():
        db_label = f"db{db_num}"
        
        # Select database if needed
        try:
            if db_num != str(original_db):
                client.execute_command("SELECT", int(db_num))
        except Exception as e:
            logger.error(f"Couldn't select database {db_num}: {e}")
            continue
        
        # Check each key
        for key_name in key_list:
            key_info = get_key_info(client, key_name)
            
            if key_info is None:
                continue
            
            key_type, size, str_val = key_info
            
            # Register key_size metric
            collector._create_metric_descr("key_size", labels=["db", "key"])
            collector._register_metric("key_size", float(size), labels={"db": db_label, "key": key_name})
            
            # Register key_value if string
            if key_type == "string" and str_val:
                try:
                    # Try to parse as float
                    val_float = float(str_val)
                    collector._create_metric_descr("key_value", labels=["db", "key"])
                    collector._register_metric("key_value", val_float, labels={"db": db_label, "key": key_name})
                except (ValueError, TypeError):
                    # Not a float, register as string label
                    collector._create_metric_descr("key_value_as_string", labels=["db", "key", "value"])
                    collector._register_metric("key_value_as_string", 1.0, 
                                             labels={"db": db_label, "key": key_name, "value": str_val})
    
    # Restore original database
    if original_db is not None:
        client.execute_command("SELECT", original_db)
