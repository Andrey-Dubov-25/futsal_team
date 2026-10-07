#!/bin/bash
set -e

# Ждём базу данных
echo "Waiting for PostgreSQL..."
python << END
import socket
import time
import os

host = os.environ.get('POSTGRES_HOST', 'db')
port = int(os.environ.get('POSTGRES_PORT', '5432'))

while True:
    try:
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        break
    except (OSError, ConnectionRefusedError):
        time.sleep(0.5)
print('PostgreSQL started')
END

# Миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Собираем статику
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Выполняем команду
exec "$@"
