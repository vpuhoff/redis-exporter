# Использование Redis Exporter как библиотеки

Redis Exporter можно использовать как библиотеку в вашем Python приложении для добавления Redis метрик к существующему Prometheus экспортеру.

## Базовое использование

```python
from prometheus_client import REGISTRY, start_http_server
from exporter import RedisCollector, Options

# Создать опции конфигурации
options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"  # Префикс для всех метрик
)

# Создать коллектор Redis
redis_collector = RedisCollector("redis://localhost:6379", options)

# Зарегистрировать в общий Prometheus Registry
REGISTRY.register(redis_collector)

# Запустить HTTP сервер
start_http_server(8080)
print("Server started on http://localhost:8080/metrics")
```

## Интеграция в существующее приложение

### Пример 1: FastAPI приложение

```python
from fastapi import FastAPI
from prometheus_client import REGISTRY, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from exporter import RedisCollector, Options

app = FastAPI()

# Ваши существующие коллекторы
Instrumentator().instrument(app).expose(app)

# Добавить Redis метрики
redis_options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)

@app.get("/metrics")
def metrics():
    return generate_latest(REGISTRY)
```

### Пример 2: Flask приложение

```python
from flask import Flask
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from exporter import RedisCollector, Options

app = Flask(__name__)

# Добавить Redis метрики
redis_options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)

@app.route("/metrics")
def metrics():
    return generate_latest(REGISTRY), 200, {"Content-Type": CONTENT_TYPE_LATEST}
```

### Пример 3: Django приложение

```python
# views.py
from django.http import HttpResponse
from prometheus_client import REGISTRY, generate_latest
from exporter import RedisCollector, Options

# Инициализация при старте приложения
redis_options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
redis_collector = RedisCollector("redis://localhost:6379", redis_options)
REGISTRY.register(redis_collector)

def metrics_view(request):
    return HttpResponse(generate_latest(REGISTRY), content_type="text/plain")
```

```python
# urls.py
from django.urls import path
from .views import metrics_view

urlpatterns = [
    path("metrics/", metrics_view, name="metrics"),
]
```

## Продвинутые примеры

### Множественные Redis серверы

```python
from prometheus_client import REGISTRY, CollectorRegistry
from exporter import RedisCollector, Options

# Каждый Redis в своем namespace
redis1_collector = RedisCollector(
    "redis://redis1:6379",
    Options(namespace="redis1")
)
REGISTRY.register(redis1_collector)

redis2_collector = RedisCollector(
    "redis://redis2:6379",
    Options(namespace="redis2")
)
REGISTRY.register(redis2_collector)
```

### Redis с аутентификацией

```python
from exporter import RedisCollector, Options

redis_collector = RedisCollector(
    "redis://localhost:6379",
    Options(
        password="secret-password",
        user="redis-user",
        namespace="redis"
    )
)
REGISTRY.register(redis_collector)
```

### Проверка конкретных ключей

```python
from exporter import RedisCollector, Options

redis_collector = RedisCollector(
    "redis://localhost:6379",
    Options(
        check_single_keys="db0=active_users,db0=total_sessions",
        check_keys="db1=user:*",
        namespace="redis"
    )
)
REGISTRY.register(redis_collector)
```

### Собственный Registry

```python
from prometheus_client import CollectorRegistry
from exporter import RedisCollector, Options

# Создать отдельный registry
custom_registry = CollectorRegistry()

# Добавить Redis метрики
redis_collector = RedisCollector(
    "redis://localhost:6379",
    Options(namespace="redis")
)
custom_registry.register(redis_collector)

# Использовать custom_registry в вашем коде
```

## API Reference

### RedisCollector

```python
collector = RedisCollector(
    redis_addr: str,      # Адрес Redis сервера
    options: Options      # Опции конфигурации
)
```

**Методы:**
- `collect()` - генератор, который возвращает MetricFamily объекты

### Options

```python
options = Options(
    redis_addr: str = "redis://localhost:6379",
    password: str = "",
    user: str = "",
    namespace: str = "redis",
    check_keys: str = "",
    check_single_keys: str = "",
    connection_timeout: float = 15.0,
    set_client_name: bool = True,
    web_listen_address: str = ":9121"
)
```

### Функции

- `connect_to_redis(...)` - создать подключение к Redis
- `do_redis_cmd(...)` - выполнить Redis команду
- `get_env(key, default)` - получить переменную окружения
- `get_env_bool(key, default)` - получить bool из окружения
- `get_env_float(key, default)` - получить float из окружения

## Установка

```bash
# Из исходников
git clone https://github.com/vpuhoff/redis-exporter.git
cd redis-exporter
pip install -e .

# Или установить зависимости напрямую
pip install redis prometheus-client
```

## Примеры метрик

После регистрации коллектора, метрики будут доступны по префиксу namespace:

- `{namespace}_up` - доступность Redis
- `{namespace}_connected_clients` - подключенные клиенты
- `{namespace}_memory_used_bytes` - использование памяти
- `{namespace}_commands_processed_total` - обработанные команды
- `{namespace}_db_keys{db="db0"}` - количество ключей в БД
- И другие...

## Best Practices

1. **Используйте уникальные namespace** для множественных Redis серверов
2. **Не забывайте про graceful shutdown** при остановке приложения
3. **Мониторьте производительность** - collector может быть медленным на больших базах
4. **Используйте connection pooling** для production
5. **Логируйте ошибки** подключения к Redis

## Troubleshooting

**Метрики не появляются:**
- Проверьте что коллектор зарегистрирован в нужном Registry
- Убедитесь что Redis доступен
- Проверьте логи приложения

**Ошибки подключения:**
- Проверьте адрес Redis (`redis://localhost:6379`)
- Проверьте аутентификацию
- Увеличьте connection_timeout

**Большое потребление памяти:**
- Отключите проверку ключей если не нужно
- Используйте check-single-keys вместо check-keys

## Дополнительные ресурсы

- 📖 [Быстрый старт](GETTING_STARTED.md) - установка и CLI использование
- 📘 [API Reference](API_REFERENCE.md) - полная документация API
- 💡 [Примеры](EXAMPLES.md) - рабочие примеры кода
- 🎨 [Дополнительные материалы](CONTRIB.md) - Grafana, Kubernetes
- 🏠 [Главная документация](README.md) - навигация по всей документации

