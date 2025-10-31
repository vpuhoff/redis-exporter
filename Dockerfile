FROM python:3.11-alpine

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir redis prometheus-client

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 59000 -S exporter && \
    adduser -S -u 59000 -G exporter exporter && \
    chown -R exporter:exporter /app

USER exporter

EXPOSE 9121

CMD ["python", "main.py"]
