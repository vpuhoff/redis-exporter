"""
Пример интеграции Redis Exporter в FastAPI приложение

Установка:
    pip install fastapi uvicorn redis prometheus-client exporter

Запуск:
    uvicorn examples.fastapi_example:app --port 8080

Метрики:
    http://localhost:8080/metrics
"""

from fastapi import FastAPI
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from exporter import RedisCollector, Options

app = FastAPI()


# Добавить Redis метрики к приложению
redis_options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)


@app.get("/")
def read_root():
    return {"message": "FastAPI with Redis Exporter"}


@app.get("/metrics")
def metrics():
    """Экспортировать Prometheus метрики включая Redis"""
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

