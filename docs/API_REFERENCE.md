# API Reference

Полная документация API Redis Exporter.

## Классы

### RedisCollector

Основной класс коллектора Prometheus метрик Redis.

```python
from exporter import RedisCollector, Options

collector = RedisCollector(redis_addr, options)
```

#### Параметры

**redis_addr** (str)
- Адрес Redis сервера (URI формат)
- Пример: `"redis://localhost:6379"`
- Поддерживает: `redis://`, `rediss://`, `unix://`

**options** (Options)
- Конфигурация экспортера
- См. [Options](#options)

#### Методы

**collect()** -> Generator[MetricFamily]
- Собирает метрики из Redis
- Возвращает генератор MetricFamily объектов
- Используется автоматически Prometheus клиентом

#### Пример

```python
from prometheus_client import REGISTRY
from exporter import RedisCollector, Options

options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis",
    check_keys=["session:*", "cache:*"]
)
collector = RedisCollector("redis://localhost:6379", options)
REGISTRY.register(collector)
```

---

### Options

Конфигурация Redis Exporter.

#### Параметры

**redis_addr** (str, default: "redis://localhost:6379")
- Адрес Redis сервера

**namespace** (str, default: "redis")
- Префикс для всех метрик

**connection_timeout** (float, default: 0.0)
- Таймаут подключения к Redis (секунды)
- 0.0 = без таймаута

**tls_cert_file** (str, default: "")
- Путь к TLS сертификату

**tls_key_file** (str, default: "")
- Путь к TLS ключу

**tls_ca_cert_file** (str, default: "")
- Путь к CA сертификату

**tls_skip_verify** (bool, default: False)
- Пропустить верификацию TLS сертификата

**check_keys** (list[str], default: [])
- Паттерны ключей для проверки (SCAN)
- Пример: `["session:*", "cache:*"]`

**check_single_keys** (list[str], default: [])
- Отдельные ключи для проверки
- Пример: `["mykey", "important:key"]`

**script** (str, default: "")
- Lua script для выполнения (не реализовано)

**client_id** (str, default: "")
- Идентификатор клиента для Redis

**log_level** (str, default: "INFO")
- Уровень логирования
- Доступные значения: `DEBUG`, `INFO`, `WARNING`, `ERROR`

#### Методы

**from_env()** -> Options
- Создает Options из переменных окружения
- См. [Переменные окружения](#переменные-окружения)

**merge_cli_args(args: argparse.Namespace)** -> Options
- Объединяет опции с CLI аргументами
- Возвращает новый Options объект

#### Пример

```python
from exporter import Options

# Программно
options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis",
    check_keys=["session:*"]
)

# Из переменных окружения
options = Options.from_env()

# Из переменных окружения с CLI аргументами
args = parse_args()
options = Options.from_env().merge_cli_args(args)
```

---

## Функции

### connect_to_redis

Создает подключение к Redis.

```python
from exporter import connect_to_redis, Options

options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis"
)
client = connect_to_redis(options.redis_addr, options)
```

#### Параметры

**redis_addr** (str)
- Адрес Redis сервера (URI формат)

**options** (Options)
- Конфигурация экспортера

#### Возвращает

**client** (redis.Redis)
- Подключенный Redis клиент

#### Пример

```python
from exporter import connect_to_redis, Options

options = Options(
    redis_addr="redis://user:pass@localhost:6379/0",
    tls_ca_cert_file="/path/to/ca.crt",
    tls_skip_verify=False
)
client = connect_to_redis(options.redis_addr, options)

# Использование
info = client.info()
```

---

### do_redis_cmd

Выполняет произвольную Redis команду с обработкой ошибок.

```python
from exporter import do_redis_cmd

result = do_redis_cmd(client, "GET", "mykey")
```

#### Параметры

**client** (redis.Redis)
- Подключенный Redis клиент

**command** (str)
- Redis команда (без аргументов)

**args** (list, optional)
- Аргументы команды

#### Возвращает

**result**
- Результат команды или `None` при ошибке

#### Пример

```python
from exporter import do_redis_cmd

# GET команда
value = do_redis_cmd(client, "GET", "mykey")

# SET команда
do_redis_cmd(client, "SET", "mykey", "myvalue")

# EXISTS команда
exists = do_redis_cmd(client, "EXISTS", "mykey")
```

---

### get_env

Получить переменную окружения как строку.

```python
from exporter import get_env

redis_addr = get_env("REDIS_ADDR", "redis://localhost:6379")
```

#### Параметры

**key** (str)
- Ключ переменной окружения

**default** (str, optional)
- Значение по умолчанию

#### Возвращает

**value** (str)
- Значение переменной окружения

---

### get_env_bool

Получить переменную окружения как boolean.

```python
from exporter import get_env_bool

debug = get_env_bool("DEBUG", False)
```

#### Параметры

**key** (str)
- Ключ переменной окружения

**default** (bool, optional)
- Значение по умолчанию

#### Возвращает

**value** (bool)
- Значение переменной окружения
- Распознает: `True`, `1`, `yes`, `on` (любой регистр)

---

### get_env_float

Получить переменную окружения как float.

```python
from exporter import get_env_float

timeout = get_env_float("CONNECTION_TIMEOUT", 5.0)
```

#### Параметры

**key** (str)
- Ключ переменной окружения

**default** (float, optional)
- Значение по умолчанию

#### Возвращает

**value** (float)
- Значение переменной окружения

---

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `REDIS_ADDR` | Адрес Redis сервера | `redis://localhost:6379` |
| `REDIS_EXPORTER_NAMESPACE` | Префикс метрик | `redis` |
| `REDIS_EXPORTER_CONNECTION_TIMEOUT` | Таймаут подключения (секунды) | `0.0` |
| `REDIS_EXPORTER_TLS_CERT_FILE` | Путь к TLS сертификату | `""` |
| `REDIS_EXPORTER_TLS_KEY_FILE` | Путь к TLS ключу | `""` |
| `REDIS_EXPORTER_TLS_CA_CERT_FILE` | Путь к CA сертификату | `""` |
| `REDIS_EXPORTER_TLS_SKIP_VERIFY` | Пропустить верификацию TLS | `false` |
| `REDIS_EXPORTER_CHECK_KEYS` | Паттерны ключей (через запятую) | `""` |
| `REDIS_EXPORTER_CHECK_SINGLE_KEYS` | Отдельные ключи (через запятую) | `""` |
| `REDIS_EXPORTER_SCRIPT` | Lua script (не реализовано) | `""` |
| `REDIS_EXPORTER_CLIENT_ID` | Идентификатор клиента | `""` |
| `REDIS_EXPORTER_LOG_LEVEL` | Уровень логирования | `INFO` |
| `REDIS_EXPORTER_INCLUDE_SYSTEM_METRICS` | Включить системные метрики | `true` |
| `REDIS_EXPORTER_PORT` | Порт HTTP сервера | `9121` |

---

## Примеры использования

### Базовое использование

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
start_http_server(9121)
```

### С проверкой ключей

```python
from exporter import RedisCollector, Options

options = Options(
    redis_addr="redis://localhost:6379",
    namespace="redis",
    check_keys=["session:*", "cache:*"],
    check_single_keys=["important:key"]
)

collector = RedisCollector("redis://localhost:6379", options)
REGISTRY.register(collector)
```

### С TLS подключением

```python
from exporter import RedisCollector, Options

options = Options(
    redis_addr="rediss://localhost:6380",
    namespace="redis",
    tls_ca_cert_file="/path/to/ca.crt",
    tls_cert_file="/path/to/client.crt",
    tls_key_file="/path/to/client.key",
    tls_skip_verify=False
)

collector = RedisCollector(options.redis_addr, options)
REGISTRY.register(collector)
```

### С переменными окружения

```python
from exporter import RedisCollector, Options

# Options автоматически читает из переменных окружения
options = Options.from_env()
collector = RedisCollector(options.redis_addr, options)
REGISTRY.register(collector)
```

### Изолированный Registry

```python
from prometheus_client import CollectorRegistry
from exporter import RedisCollector, Options

# Создать отдельный Registry
registry = CollectorRegistry()

# Создать коллектор
options = Options(redis_addr="redis://localhost:6379", namespace="redis")
collector = RedisCollector("redis://localhost:6379", options)

# Зарегистрировать в изолированном Registry
registry.register(collector)

# Экспортировать метрики
from prometheus_client import generate_latest
metrics = generate_latest(registry)
```

---

## Экспортируемые метрики

### Основные метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| `redis_up` | Gauge | Доступность Redis (0 или 1) |
| `redis_exporter_scrape_duration_seconds` | Gauge | Время сбора метрик |
| `redis_exporter_last_scrape_error` | Gauge | Ошибка последнего сбора |

### INFO метрики

Полный список метрик из команды `INFO` Redis.

Основные категории:
- **Server**: `redis_version`, `redis_mode`, `os`
- **Clients**: `connected_clients`, `blocked_clients`
- **Memory**: `used_memory`, `used_memory_human`, `maxmemory`
- **Stats**: `total_commands_processed`, `instantaneous_ops_per_sec`
- **Replication**: `role`, `master_repl_offset`, `slave0:...`
- **Keyspace**: `db0:keys`, `db0:expires`, `db0:avg_ttl`

### Key метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| `redis_key_size` | Gauge | Размер ключа в байтах |
| `redis_key_value` | Gauge | Значение ключа (если числовое) |
| `redis_keys_count` | Gauge | Количество ключей по паттерну |

Все метрики имеют префикс из `options.namespace` (по умолчанию `redis_`).

---

## Дополнительные ресурсы

- 📖 [Быстрый старт](GETTING_STARTED.md) - установка и CLI использование
- 📚 [Использование как библиотека](LIBRARY_USAGE.md) - подробная документация API
- 💡 [Примеры](EXAMPLES.md) - рабочие примеры использования
- 🎨 [Дополнительные материалы](CONTRIB.md) - Grafana dashboards, Kubernetes
- 🏠 [Главная документация](README.md) - навигация по всей документации

