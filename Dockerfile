# Этап 1: Сборка зависимостей
FROM python:3.12-slim as builder

WORKDIR /app

# Установка необходимых системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.12-slim

WORKDIR /app

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && \
    mkdir -p /images /logs /static && \
    chown -R appuser:appuser /app /images /logs /static

# Копирование зависимостей из этапа сборки
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование кода приложения
COPY app.py .

# Переключение на непривилегированного пользователя
USER appuser

# Переменные окружения
ENV PORT=8000
ENV HOST=0.0.0.0

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["python", "-u", "app.py"]