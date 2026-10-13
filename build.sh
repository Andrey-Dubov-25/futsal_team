#!/usr/bin/env bash
# Build script for Render

set -o errexit   # Остановка при ошибке
set -o pipefail  # Ошибка в pipe
set -o nounset   # Ошибка при неопределённой переменной

echo "=== Установка зависимостей ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Сбор статики ==="
python manage.py collectstatic --no-input --clear

echo "=== Применение миграций ==="
python manage.py migrate --no-input

echo "=== Готово ==="
