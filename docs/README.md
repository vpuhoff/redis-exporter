# Redis Exporter - Документация

Добро пожаловать в документацию Redis Exporter (Python версия)!

## Содержание

### [Быстрый старт](GETTING_STARTED.md)
Основная документация по установке и использованию Redis Exporter.

- Установка и требования
- Основное использование (CLI)
- Docker deployment
- Конфигурация через переменные окружения
- Доступные флаги командной строки
- Экспортируемые метрики
- Примеры использования

### [Использование как библиотека](LIBRARY_USAGE.md)
Инструкции по интеграции Redis Exporter в ваше Python приложение.

- Базовое использование
- Интеграция в FastAPI приложение
- Интеграция в Flask приложение
- Интеграция в Django приложение
- Работа с несколькими Redis серверами
- Использование custom Registry
- Troubleshooting

### [API Reference](API_REFERENCE.md)
Полная документация API.

- RedisCollector - основной коллектор
- Options - конфигурация
- Вспомогательные функции
- Переменные окружения
- Примеры использования
- Экспортируемые метрики

### [Примеры](EXAMPLES.md)
Рабочие примеры использования библиотеки в различных сценариях.

- simple_example.py - минимальный пример
- fastapi_example.py - интеграция с FastAPI
- flask_example.py - интеграция с Flask
- multiple_redis_example.py - мониторинг нескольких Redis
- custom_registry_example.py - изолированный Registry

### [Дополнительные материалы](CONTRIB.md)
Дополнительные файлы и конфигурации.

- Grafana dashboards
- Kubernetes deployment
- Описание всех contrib файлов

## Быстрая навигация

### Для начинающих
1. Начните с [Быстрого старта](GETTING_STARTED.md)
2. Попробуйте [примеры](EXAMPLES.md)
3. Прочитайте [интеграцию библиотеки](LIBRARY_USAGE.md) если нужно

### Для интеграции в проект
1. Прочитайте [Использование как библиотека](LIBRARY_USAGE.md)
2. Посмотрите [примеры интеграции](EXAMPLES.md)
3. Адаптируйте под свой фреймворк

### Для production
1. Изучите [Kubernetes deployment](CONTRIB.md#kubernetes-deployment)
2. Настройте [Grafana dashboards](CONTRIB.md#grafana-dashboards)
3. Настройте мониторинг в Prometheus

## Обратная связь

Если у вас возникли вопросы или проблемы:
- Откройте [Issue](https://github.com/oliver006/redis_exporter/issues)
- Участвуйте в [Discussions](https://github.com/oliver006/redis_exporter/discussions)

## Лицензия

MIT License - см. [LICENSE](../LICENSE)

