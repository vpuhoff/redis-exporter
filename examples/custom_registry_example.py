"""
Пример использования с отдельным Registry

Полезно когда нужно изолировать Redis метрики от остальных

Запуск:
    python examples/custom_registry_example.py

Метрики:
    http://localhost:8080/redis_metrics
"""

from flask import Flask
from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from exporter import RedisCollector, Options

app = Flask(__name__)

# Создать отдельный registry для Redis метрик
redis_registry = CollectorRegistry()

# Добавить Redis метрики
redis_options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
redis_registry.register(redis_collector)


@app.route("/")
def index():
    return """
    <h1>Custom Registry Example</h1>
    <ul>
        <li><a href="/redis_metrics">Redis Metrics</a></li>
        <li><a href="/app_metrics">App Metrics (если есть)</a></li>
    </ul>
    """


@app.route("/redis_metrics")
def redis_metrics():
    """Только Redis метрики из отдельного registry"""
    return generate_latest(redis_registry), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    print("Redis metrics available at: http://localhost:8080/redis_metrics")
    app.run(host="0.0.0.0", port=8080, debug=False)

