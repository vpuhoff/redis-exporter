"""Redis client connection module"""

import logging
from typing import Optional
from urllib.parse import urlparse

import redis

logger = logging.getLogger(__name__)


def connect_to_redis(
    redis_addr: str,
    password: str = "",
    user: str = "",
    connection_timeout: float = 15.0,
    set_client_name: bool = True,
) -> redis.Redis:
    """
    Connect to Redis instance
    
    Args:
        redis_addr: Redis URI (redis://host:port or rediss:// for TLS)
        password: Password for authentication
        user: Username for authentication (Redis 6.0+ ACL)
        connection_timeout: Connection timeout in seconds
        set_client_name: Whether to set client name to redis_exporter
    
    Returns:
        redis.Redis instance
    """
    # Parse URI
    uri = redis_addr
    if "://" not in uri:
        uri = f"redis://{uri}"
    
    # Detect TLS
    use_tls = uri.startswith("rediss://")
    
    # Parse connection parameters from URI
    parsed = urlparse(uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    
    # Extract password from URI if not provided separately
    url_password = password
    if parsed.password:
        url_password = parsed.password
    
    # Parse username from URI
    url_user = user
    if parsed.username:
        url_user = parsed.username
    
    logger.debug(f"Connecting to Redis: {host}:{port}, user={url_user}, tls={use_tls}")
    
    # Create connection parameters
    conn_params = {
        "host": host,
        "port": port,
        "password": url_password,
        "socket_timeout": connection_timeout,
        "socket_connect_timeout": connection_timeout,
        "decode_responses": False,  # Get raw bytes for better compatibility
    }
    
    if url_user:
        conn_params["username"] = url_user
    
    if use_tls:
        conn_params["ssl"] = True
        # Skip SSL verification for basic use case
        conn_params["ssl_cert_reqs"] = None
    
    # Create Redis client
    client = redis.Redis(**conn_params)
    
    # Set client name if requested
    if set_client_name:
        try:
            client.client_setname("redis_exporter")
        except Exception as e:
            logger.warning(f"Failed to set client name: {e}")
    
    # Test connection with PING
    try:
        client.ping()
        logger.info(f"Successfully connected to Redis at {host}:{port}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    return client


def do_redis_cmd(client: redis.Redis, cmd: str, *args) -> Optional[object]:
    """
    Execute Redis command
    
    Args:
        client: Redis client
        cmd: Command name
        *args: Command arguments
    
    Returns:
        Command result
    """
    logger.debug(f"Executing Redis command: {cmd} args: {args}")
    try:
        result = client.execute_command(cmd, *args)
        logger.debug(f"Command completed successfully")
        return result
    except Exception as e:
        logger.error(f"Command failed: {e}")
        raise

