"""Configuration options for the Redis Exporter"""

import os
from dataclasses import dataclass


def get_env(key: str, default: str = "") -> str:
    """Get environment variable or return default"""
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable"""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


@dataclass
class Options:
    """Configuration options for Redis Exporter"""

    # Redis connection
    redis_addr: str = "redis://localhost:6379"
    password: str = ""
    user: str = ""

    # Metrics configuration
    namespace: str = "redis"
    
    # Key checking
    check_keys: str = ""
    check_single_keys: str = ""
    
    # Connection settings
    connection_timeout: float = 15.0
    set_client_name: bool = True
    
    # HTTP server
    web_listen_address: str = ":9121"
    
    @classmethod
    def from_env(cls) -> "Options":
        """Create Options from environment variables"""
        return cls(
            redis_addr=get_env("REDIS_ADDR", "redis://localhost:6379"),
            password=get_env("REDIS_PASSWORD", ""),
            user=get_env("REDIS_USER", ""),
            namespace=get_env("REDIS_EXPORTER_NAMESPACE", "redis"),
            check_keys=get_env("REDIS_EXPORTER_CHECK_KEYS", ""),
            check_single_keys=get_env("REDIS_EXPORTER_CHECK_SINGLE_KEYS", ""),
            connection_timeout=get_env_float("REDIS_EXPORTER_CONNECTION_TIMEOUT", 15.0),
            set_client_name=get_env_bool("REDIS_EXPORTER_SET_CLIENT_NAME", True),
            web_listen_address=get_env("REDIS_EXPORTER_WEB_LISTEN_ADDRESS", ":9121"),
        )
    
    def merge_cli_args(self, **kwargs) -> None:
        """Merge command-line arguments into options"""
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

