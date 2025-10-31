"""
Пример использования с несколькими Redis серверами

Установка:
    pip install redis prometheus-client

Запуск:
    # Сначала запустите Redis на разных портах
    docker run -d --name redis1 -p 6379:6379 redis:7.4
    docker run -d --name redis2 -p 6380:6379 redis:7.4
    
    python examples/multiple_redis_example.py

Метрики:
    http://localhost:8080/metrics
"""

from prometheus_client import REGISTRY, start_http_server
from exporter import RedisCollector, Options

def main():
    # Redis 1 - основной
    redis1_options = Options(
        redis_addr="redis://localhost:6379",
        namespace="redis_primary",
        check_keys="db0=user:*"
    )
    redis1_collector = RedisCollector("redis://localhost:6379", redis1_options)
    REGISTRY.register(redis1_collector)
    
    # Redis 2 - кэш
    redis2_options = Options(
        redis_addr="redis://localhost:6380",
        namespace="redis_cache",
        check_single_keys="db0=cache_stats"
    )
    redis2_collector = RedisCollector("redis://localhost:6380", redis2_options)
    REGISTRY.register(redis2_collector)
    
    print("Starting Redis Exporter with multiple servers")
    print("- Primary Redis (namespace: redis_primary): localhost:6379")
    print("- Cache Redis (namespace: redis_cache): localhost:6380")
    print("\nMetrics available at: http://localhost:8080/metrics")
    
    # Запустить HTTP сервер
    start_http_server(8080)
    
    # Держать программу запущенной
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()

