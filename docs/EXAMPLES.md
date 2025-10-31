# Примеры использования Redis Exporter как библиотеки

Эта папка содержит примеры интеграции Redis Exporter в различные Python приложения.

## Примеры

### simple_example.py

Минимальный пример использования библиотеки.

```bash
python examples/simple_example.py
```

Показывает базовую интеграцию с простым HTTP сервером.

### fastapi_example.py

Интеграция в FastAPI приложение.

**Установка:**
```bash
pip install fastapi uvicorn
```

**Запуск:**
```bash
uvicorn examples.fastapi_example:app --port 8080
```

**Метрики:** http://localhost:8080/metrics

### flask_example.py

Интеграция в Flask приложение.

**Установка:**
```bash
pip install flask
```

**Запуск:**
```bash
python examples/flask_example.py
```

**Метрики:** http://localhost:8080/metrics

### multiple_redis_example.py

Работа с несколькими Redis серверами одновременно.

**Требования:** Redis на портах 6379 и 6380

**Запуск:**
```bash
# Запустите Redis на разных портах
docker run -d --name redis1 -p 6379:6379 redis:7.4
docker run -d --name redis2 -p 6380:6379 redis:7.4

python examples/multiple_redis_example.py
```

Показывает как использовать разные namespace для разных Redis инстансов.

### custom_registry_example.py

Использование отдельного Prometheus Registry для изоляции метрик.

**Запуск:**
```bash
python examples/custom_registry_example.py
```

**Метрики:**
- Redis: http://localhost:8080/redis_metrics
- App: http://localhost:8080/app_metrics

## Использование в своем проекте

### Базовый пример

```python
from prometheus_client import REGISTRY, start_http_server
from exporter import RedisCollector, Options

# Создать опции
options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)

# Создать коллектор
collector = RedisCollector("redis://localhost:6379", options)

# Зарегистрировать
REGISTRY.register(collector)

# Запустить сервер
start_http_server(8080)
```

### С FastAPI

```python
from fastapi import FastAPI
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from exporter import RedisCollector, Options

app = FastAPI()

# Добавить Redis метрики
redis_options = Options(redis_addr="redis://localhost:6379", namespace="redis")
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )
```

### С Flask

```python
from flask import Flask
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from exporter import RedisCollector, Options

app = Flask(__name__)

# Добавить Redis метрики
redis_options = Options(redis_addr="redis://localhost:6379", namespace="redis")
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)

@app.route("/metrics")
def metrics():
    return generate_latest(REGISTRY), 200, {"Content-Type": CONTENT_TYPE_LATEST}
```

## Дополнительная документация

См. [README_LIBRARY.md](../README_LIBRARY.md) для подробной документации по использованию библиотеки.

## Требования

Все примеры требуют:
- Python 3.11+
- redis
- prometheus-client

Специфичные зависимости указаны в комментариях каждого примера.

## Дополнительные ресурсы

- 📖 [Быстрый старт](GETTING_STARTED.md) - установка и CLI использование
- 📚 [Использование как библиотека](LIBRARY_USAGE.md) - интеграция в приложения
- 📘 [API Reference](API_REFERENCE.md) - полная документация API
- 🎨 [Дополнительные материалы](CONTRIB.md) - Grafana dashboards, Kubernetes
- 🏠 [Главная документация](README.md) - навигация по всей документации

