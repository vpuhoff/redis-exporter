"""
Простой пример использования Redis Exporter как библиотеки

Установка:
    pip install redis prometheus-client

Запуск:
    python examples/simple_example.py

Метрики:
    http://localhost:8080/metrics
"""

from prometheus_client import REGISTRY, start_http_server
from exporter import RedisCollector, Options

def main():
    # Создать опции конфигурации
    options = Options(
        redis_addr="redis://localhost:6379",
        namespace="redis"
    )
    
    # Создать коллектор Redis
    redis_collector = RedisCollector("redis://localhost:6379", options)
    
    # Зарегистрировать в Prometheus
    REGISTRY.register(redis_collector)
    
    # Запустить HTTP сервер
    print("Starting Redis Exporter on http://localhost:8080/metrics")
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

