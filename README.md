# Futsal Team

![CI](https://github.com/Andrey-Dubov-25/futsal_team/actions/workflows/ci.yml/badge.svg)

Сайт мини-футбольной команды: расписание матчей, состав, статистика игроков, новости, фотогалерея.

## Стек

- **Python** 3.12
- **Django** 5.1.1
- **Django REST Framework** — API
- **PostgreSQL** 16
- **Docker** + Docker Compose
- **JWT** — авторизация через `djangorestframework-simplejwt`
- **OpenAPI / Swagger** — документация API через `drf-spectacular`
- **django-filter** — фильтрация, поиск, сортировка
- **pytest** + **factory-boy** — тесты
- **ruff** + **bandit** + **pre-commit** — качество кода
- **GitHub Actions** — CI

## Быстрый старт

### Требования

- Docker Desktop
- Python 3.12 (для локальных инструментов — pre-commit, ruff)
- Git
- GNU Make (на Windows — через `pip install gnumake` или Chocolatey/Scoop)

### Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Andrey-Dubov-25/futsal_team.git
cd futsal_team

# 2. Создать .env из шаблона
cp .env.example .env

# 3. Поднять контейнеры
docker compose up -d --build

# 4. Применить миграции
docker compose exec web python manage.py migrate

# 5. Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# 6. (Опционально) Установить dev-инструменты локально
python -m venv .venv
source .venv/Scripts/activate   # Windows / Git Bash
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements-dev.txt
pre-commit install



### Продакшн (на сервере)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Andrey-Dubov-25/futsal_team.git
cd futsal_team

# 2. Создать .env.prod
cp .env.prod.example .env.prod
nano .env.prod  # заменить SECRET_KEY, пароль БД, домен

# 3. Сгенерировать SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Поднять
docker compose -f docker-compose.prod.yml up -d --build

# 5. Создать суперпользователя
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Проверка
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
