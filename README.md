# Prometheus Redis Exporter (Python версия)

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Prometheus экспортер для метрик Redis/Valkey, написанный на Python.

## Описание

Это Python-версия [redis_exporter](https://github.com/oliver006/redis_exporter) от [oliver006](https://github.com/oliver006), предоставляющая базовый функционал для экспорта метрик Redis в формате Prometheus.

**Оригинальный проект:** [https://github.com/oliver006/redis_exporter](https://github.com/oliver006/redis_exporter)  
**Текущий проект:** [https://github.com/vpuhoff/redis-exporter](https://github.com/vpuhoff/redis-exporter)

### Реализованные возможности

- ✅ Экспорт метрик через команду INFO
- ✅ Поддержка проверки отдельных ключей
- ✅ Поддержка паттернов ключей через SCAN
- ✅ TLS соединения
- ✅ Базовая аутентификация (username/password)
- ✅ Graceful shutdown
- ✅ Prometheus client library

### Не реализовано (ограничения)

- ❌ Multi-target scrape endpoint (`/scrape`)
- ❌ Cluster discovery (`/discover-cluster-nodes`)
- ❌ Поддержка кластеров Redis
- ❌ Поддержка Sentinel
- ❌ Stream metrics
- ❌ Lua scripts
- ❌ Key groups aggregation
- ❌ Latency histograms

## Требования

- Python 3.11+
- Redis 2.x - 8.x

## Установка

### Установка как пакет

```bash
# Из исходников
git clone https://github.com/vpuhoff/redis-exporter.git
cd redis-exporter
pip install -e .

# Или установить зависимости напрямую
pip install redis prometheus-client
```

### Использование в вашем проекте

Если у вас уже есть Python проект с Prometheus метриками, вы можете использовать Redis Exporter как библиотеку:

```python
from prometheus_client import REGISTRY
from exporter import RedisCollector, Options

# Создать и зарегистрировать Redis коллектор
options = Options(redis_addr="redis://localhost:6379", namespace="redis")
redis_collector = RedisCollector("redis://localhost:6379", options)
REGISTRY.register(redis_collector)
```

См. [README_LIBRARY.md](README_LIBRARY.md) для подробных примеров интеграции в FastAPI, Flask, Django и другие фреймворки.

## Использование

### Базовый запуск

```bash
python main.py --redis.addr=redis://localhost:6379
```

### С опциями

```bash
python main.py \
  --redis.addr=redis://localhost:6379 \
  --redis.password=mypassword \
  --check-keys="db0=user:*,db1=sessions:*" \
  --check-single-keys="db0=counter" \
  --log-level=DEBUG
```

### Переменные окружения

```bash
export REDIS_ADDR=redis://localhost:6379
export REDIS_PASSWORD=mypassword
export REDIS_EXPORTER_CHECK_KEYS="db0=test:*"
export REDIS_EXPORTER_LOG_LEVEL=INFO

python main.py
```

## Docker

### Сборка образа

```bash
docker build -t redis-exporter-py .
```

### Запуск контейнера

```bash
docker run -d \
  --name redis-exporter \
  -p 9121:9121 \
  -e REDIS_ADDR=redis://redis-host:6379 \
  redis-exporter-py
```

### Docker Compose

```bash
# Запустить тестовое окружение
docker-compose -f docker-compose-py.yml up -d

# Проверить метрики
curl http://localhost:9121/metrics
```

## Конфигурация Prometheus

Добавьте в `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: redis_exporter
    static_configs:
    - targets: ['localhost:9121']
```

## Доступные флаги

| Флаг | Переменная окружения | Описание |
|------|---------------------|----------|
| `--redis.addr` | `REDIS_ADDR` | Адрес Redis (по умолчанию: `redis://localhost:6379`) |
| `--redis.user` | `REDIS_USER` | Имя пользователя для аутентификации |
| `--redis.password` | `REDIS_PASSWORD` | Пароль для аутентификации |
| `--namespace` | `REDIS_EXPORTER_NAMESPACE` | Namespace для метрик (по умолчанию: `redis`) |
| `--check-keys` | `REDIS_EXPORTER_CHECK_KEYS` | Паттерны ключей для проверки через SCAN |
| `--check-single-keys` | `REDIS_EXPORTER_CHECK_SINGLE_KEYS` | Конкретные ключи для проверки |
| `--connection-timeout` | `REDIS_EXPORTER_CONNECTION_TIMEOUT` | Таймаут подключения в секундах |
| `--web.listen-address` | `REDIS_EXPORTER_WEB_LISTEN_ADDRESS` | Адрес HTTP сервера |
| `--log-level` | `REDIS_EXPORTER_LOG_LEVEL` | Уровень логирования (DEBUG/INFO/WARNING/ERROR) |
| `--log-format` | `REDIS_EXPORTER_LOG_FORMAT` | Формат логов (txt/json) |
| `--debug` | - | Включить отладочный вывод |
| `--version` | - | Показать версию и выйти |

## Экспортируемые метрики

### Базовые метрики

- `redis_up` - доступность Redis
- `redis_exporter_scrapes_total` - общее количество сканирований
- `redis_exporter_scrape_duration_seconds` - длительность сканирования
- `redis_exporter_last_scrape_error` - ошибка последнего сканирования

### Метрики Redis INFO

Основные категории метрик из команды INFO:

- **Server**: uptime, процесс, потоки
- **Clients**: подключенные клиенты, заблокированные клиенты
- **Memory**: использование памяти, RSS, пиковое использование
- **Stats**: операции в секунду, команды
- **Replication**: статус репликации, offset
- **Keyspace**: количество ключей по БД

### Метрики ключей

При использовании `--check-keys` или `--check-single-keys`:

- `redis_key_size` - размер ключа (количество элементов)
- `redis_key_value` - значение ключа (если числовое)
- `redis_key_value_as_string` - значение ключа как строка

## Примеры использования

### Мониторинг одного Redis

```bash
python main.py --redis.addr=redis://localhost:6379
```

### Мониторинг с паролем

```bash
python main.py \
  --redis.addr=redis://localhost:6379 \
  --redis.password=secret
```

### Мониторинг с проверкой ключей

```bash
python main.py \
  --redis.addr=redis://localhost:6379 \
  --check-single-keys="db0=active_users,db0=total_sessions" \
  --check-keys="db1=user:*"
```

### TLS соединение

```bash
python main.py --redis.addr=rediss://localhost:6380
```

## Тестирование

```bash
# Установить зависимости для разработки
uv pip install -e .

# Запустить тесты (если есть)
# pytest tests/

# Проверить метрики
curl http://localhost:9121/metrics
```

## Разработка

### Структура проекта

```
redis-exporter/
├── main.py                  # Точка входа (CLI)
├── pyproject.toml           # Зависимости Python
├── Dockerfile               # Docker образ
├── docker-compose.yml       # Docker Compose для тестирования
├── README.md                # Основная документация
├── README_LIBRARY.md        # Документация для использования как библиотека
├── .gitignore               # Git ignore файлы
├── LICENSE                  # MIT лицензия
├── exporter/                # Модули экспортера
│   ├── __init__.py
│   ├── config.py            # Конфигурация
│   ├── exporter.py          # Главный коллектор
│   ├── info.py              # Парсинг INFO
│   ├── keys.py              # Проверка ключей
│   ├── metrics.py           # Вспомогательные функции
│   └── redis_client.py      # Redis клиент
├── examples/                # Примеры использования как библиотеки
│   ├── __init__.py
│   ├── simple_example.py
│   ├── fastapi_example.py
│   ├── flask_example.py
│   ├── multiple_redis_example.py
│   └── custom_registry_example.py
└── contrib/                 # Дополнительные материалы
    ├── README.md            # Описание contrib
    ├── grafana_prometheus_redis_dashboard.json
    ├── grafana_prometheus_redis_dashboard_exporter_version_0.3x.json
    └── k8s-redis-and-exporter-deployment.yaml
```

### Добавление новых метрик

1. Добавьте метрику в `metric_map_gauges` или `metric_map_counters` в `exporter/exporter.py`
2. Запустите тесты
3. Обновите документацию

## Ограничения по сравнению с Go-версией

- Одновременный мониторинг только одного Redis
- Нет поддержки кластеров
- Нет поддержки Sentinel
- Нет многопоточности для SCAN
- Более медленная работа на больших нагрузках

## Использование как библиотека

Redis Exporter может использоваться в вашем Python приложении для добавления Redis метрик к существующим Prometheus метрикам:

```python
from prometheus_client import REGISTRY
from exporter import RedisCollector, Options

# Создать и зарегистрировать коллектор
options = Options(redis_addr="redis://localhost:6379", namespace="redis")
collector = RedisCollector("redis://localhost:6379", options)
REGISTRY.register(collector)
```

**📚 Полная документация:** См. папку [docs/](docs/) со всей документацией проекта.

- [Быстрый старт](docs/GETTING_STARTED.md) - установка и CLI использование
- [Использование как библиотека](docs/LIBRARY_USAGE.md) - интеграция в приложения
- [Примеры](docs/EXAMPLES.md) - рабочие примеры использования
- [Дополнительные материалы](docs/CONTRIB.md) - Grafana dashboards, Kubernetes

## Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## Благодарности

Этот проект основан на [oliver006/redis_exporter](https://github.com/oliver006/redis_exporter).

## Контрибуции

Приветствуются! Откройте issue или создайте pull request.

## Поддержка

- [Issues](https://github.com/vpuhoff/redis-exporter/issues)
- [Discussions](https://github.com/vpuhoff/redis-exporter/discussions)

