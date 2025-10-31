"""
Пример интеграции Redis Exporter в Flask приложение

Установка:
    pip install flask redis prometheus-client exporter

Запуск:
    python examples/flask_example.py

Метрики:
    http://localhost:8080/metrics
"""

from flask import Flask
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from exporter import RedisCollector, Options

app = Flask(__name__)


# Добавить Redis метрики к приложению
redis_options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)


@app.route("/")
def index():
    return "<h1>Flask with Redis Exporter</h1>"


@app.route("/metrics")
def metrics():
    """Экспортировать Prometheus метрики включая Redis"""
    return generate_latest(REGISTRY), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

