# Prometheus Redis Exporter (Python версия)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-118%20passed-green.svg)](tests/)

Prometheus экспортер для метрик Redis/Valkey, написанный на Python.

**Основной проект:** [Python версия](#) | [Оригинал (Go)](https://github.com/oliver006/redis_exporter)

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

- Python 3.10+
- Redis 2.x - 8.x

## Установка

### Установка из PyPI

```bash
# Установка из PyPI (после публикации)
pip install redis-exporter

# Или с uv
uv pip install redis-exporter
```

### Установка как пакет

```bash
# Из исходников
git clone https://github.com/vpuhoff/redis-exporter.git
cd redis-exporter
pip install -e .

# Или с uv
uv sync
```

## Использование

### Базовый запуск (после установки из исходников)

```bash
# Из исходников
python main.py --redis.addr=redis://localhost:6379

# После установки из PyPI
redis-exporter --redis.addr=redis://localhost:6379
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
docker-compose up -d

# Проверить метрики
curl http://localhost:9121/metrics

# Остановить
docker-compose down
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

Проект имеет comprehensive набор unit и integration тестов:

```bash
# Запустить все тесты
pytest

# Запустить только unit тесты
pytest -m unit

# Запустить только integration тесты (требуют Redis)
pytest -m integration

# Запустить тесты с coverage report
pytest --cov=exporter --cov-report=html

# Проверить метрики
curl http://localhost:9121/metrics
```

### Coverage

Текущее покрытие тестами: **77%**

Все основные модули покрыты тестами:
- config.py: 100%
- metrics.py: 98%
- info.py: 93%
- redis_client.py: 100%
- exporter.py: 45%
- keys.py: 55%

## Разработка

### Структура проекта

```
redis-exporter/
├── main.py                  # Точка входа (CLI)
├── pyproject.toml           # Зависимости Python
├── uv.lock                  # UV lock file
├── Dockerfile               # Docker образ
├── docker-compose.yml       # Docker Compose для тестирования
├── README.md                # Основная документация
├── .gitignore               # Git ignore файлы
├── LICENSE                  # MIT лицензия
├── exporter/                # Модули экспортера
│   ├── __init__.py
│   ├── _version.py          # Автоматическая версия
│   ├── config.py            # Конфигурация
│   ├── exporter.py          # Главный коллектор
│   ├── info.py              # Парсинг INFO
│   ├── keys.py              # Проверка ключей
│   ├── metrics.py           # Вспомогательные функции
│   └── redis_client.py      # Redis клиент
├── examples/                # Примеры использования как библиотеки
│   ├── __init__.py
│   ├── README.md
│   ├── simple_example.py
│   ├── fastapi_example.py
│   ├── flask_example.py
│   ├── multiple_redis_example.py
│   └── custom_registry_example.py
├── tests/                   # Тесты
│   ├── unit/               # Unit тесты
│   ├── integration/        # Integration тесты
│   ├── conftest.py
│   └── utils.py
├── docs/                    # Документация
│   ├── README.md
│   ├── GETTING_STARTED.md
│   ├── LIBRARY_USAGE.md
│   ├── API_REFERENCE.md
│   ├── EXAMPLES.md
│   └── CONTRIB.md
└── contrib/                 # Дополнительные материалы
    ├── README.md
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
- [API Reference](docs/API_REFERENCE.md) - полная документация API
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

