FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пустого __init__.py в корневой директории
RUN touch __init__.py

# Создание скрипта запуска
RUN echo '#!/bin/bash\n\
python -m alembic upgrade head\n\
python main.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Создание непривилегированного пользователя
RUN useradd -m botuser && \
    chown -R botuser:botuser /app
USER botuser

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Запуск приложения через скрипт
CMD ["/app/start.sh"] 