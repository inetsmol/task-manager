# Dockerfile
FROM python:3.12-slim

# --- Базовые настройки окружения ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- Установим системные зависимости по минимуму (curl для healthcheck) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

# --- Устанавливаем зависимости из requirements.txt ---
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Копируем исходники приложения ---
COPY app /app/app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -fsS http://localhost:8000/ || exit 1

# --- Запуск Uvicorn ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
