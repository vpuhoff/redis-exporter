# Contrib

Дополнительные материалы для Redis Exporter.

## Grafana Dashboards

### `grafana_prometheus_redis_dashboard.json`
Основной дашборд для Prometheus Redis Exporter 1.x.

**Установка:**
1. Откройте Grafana
2. Перейдите в Dashboards -> Import
3. Загрузите файл `grafana_prometheus_redis_dashboard.json`
4. Выберите datasource Prometheus

**Метрики:**
- Uptime
- Total memory use
- Connected clients
- Commands processed
- Replication lag
- Keyspace information
- И другие

### `grafana_prometheus_redis_dashboard_exporter_version_0.3x.json`
Устаревший дашборд для версии экспортера 0.3.x. Используйте только для совместимости.

## Kubernetes Deployment

### `k8s-redis-and-exporter-deployment.yaml`

Пример deployment для Kubernetes, который запускает Redis и Redis Exporter как sidecar контейнеры в одном pod.

**Использование:**
```bash
kubectl apply -f contrib/k8s-redis-and-exporter-deployment.yaml
```

**Важно:**
- Измените `YOUR_IMAGE/redis_exporter:latest` на ваш образ
- Настройте переменные окружения под вашу конфигурацию Redis
- Prometheus автоматически обнаружит exporter через аннотации

**Переменные окружения:**
- `REDIS_ADDR` - адрес Redis (по умолчанию: redis://localhost:6379)
- `REDIS_PASSWORD` - пароль Redis (если требуется)
- `REDIS_EXPORTER_LOG_LEVEL` - уровень логирования (INFO, DEBUG, WARNING, ERROR)

**Безопасность:**
- Использует non-root пользователя (UID 59000)
- Минимальные capabilities
- Dropped privileges

## Дополнительные ресурсы

- 📖 [Быстрый старт](GETTING_STARTED.md) - установка и CLI использование
- 📚 [Использование как библиотека](LIBRARY_USAGE.md) - интеграция в приложения
- 📘 [API Reference](API_REFERENCE.md) - полная документация API
- 💡 [Примеры](EXAMPLES.md) - рабочие примеры использования
- 🏠 [Главная документация](README.md) - навигация по всей документации

