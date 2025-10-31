"""Redis Exporter for Prometheus - Python version

Использование как библиотеки:

    from prometheus_client import REGISTRY
    from exporter import RedisCollector, Options
    
    # Создать опции
    options = Options(
        redis_addr="redis://localhost:6379",
        namespace="redis"
    )
    
    # Создать коллектор
    collector = RedisCollector("redis://localhost:6379", options)
    
    # Зарегистрировать в Prometheus
    REGISTRY.register(collector)

Или использовать как CLI:

    $ python -m exporter --redis.addr=redis://localhost:6379
"""

__version__ = "1.0.0"

from .config import Options, get_env, get_env_bool, get_env_float
from .exporter import RedisCollector
from .redis_client import connect_to_redis, do_redis_cmd

__all__ = [
    "RedisCollector",
    "Options",
    "connect_to_redis",
    "do_redis_cmd",
    "get_env",
    "get_env_bool",
    "get_env_float",
]
