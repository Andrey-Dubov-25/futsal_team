.DEFAULT_GOAL := help

# =============================================================================
# Переменные
# =============================================================================

DC := docker compose
WEB := $(DC) exec web
RUN := $(DC) run --rm

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help: ## Показать список команд
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# Docker
# =============================================================================

.PHONY: up
up: ## Поднять контейнеры в фоне
	$(DC) up -d

.PHONY: down
down: ## Остановить контейнеры
	$(DC) down

.PHONY: build
build: ## Пересобрать образы и поднять
	$(DC) up -d --build

.PHONY: restart
restart: ## Перезапустить web-контейнер
	$(DC) restart web

.PHONY: ps
ps: ## Показать статус контейнеров
	$(DC) ps

.PHONY: logs
logs: ## Логи web (follow)
	$(DC) logs -f --tail=50 web

.PHONY: logs-db
logs-db: ## Логи db (follow)
	$(DC) logs -f --tail=50 db

.PHONY: sh
sh: ## Bash внутри web-контейнера
	$(WEB) bash

# =============================================================================
# Django
# =============================================================================

.PHONY: shell
shell: ## Django shell
	$(WEB) python manage.py shell

.PHONY: mm
mm: ## Создать миграции
	$(WEB) python manage.py makemigrations

.PHONY: migrate
migrate: ## Применить миграции
	$(WEB) python manage.py migrate

.PHONY: superuser
superuser: ## Создать суперпользователя
	$(WEB) python manage.py createsuperuser

.PHONY: check
check: ## Django check
	$(WEB) python manage.py check

.PHONY: collectstatic
collectstatic: ## Собрать статику
	$(WEB) python manage.py collectstatic --noinput

# =============================================================================
# Quality
# =============================================================================

.PHONY: lint
lint: ## Прогнать pre-commit по всем файлам
	pre-commit run --all-files

.PHONY: lint-staged
lint-staged: ## Прогнать pre-commit по staged-файлам
	pre-commit run

.PHONY: format
format: ## Отформатировать код ruff-ом
	ruff format apps config

.PHONY: fix
fix: ## ruff: авто-исправления
	ruff check --fix apps config

# =============================================================================
# Tests
# =============================================================================

.PHONY: test
test: ## Прогнать тесты
	$(WEB) pytest

.PHONY: test-cov
test-cov: ## Тесты с покрытием
	$(WEB) pytest --cov=apps --cov-report=term-missing --cov-report=html

.PHONY: test-fast
test-fast: ## Тесты без покрытия, стоп на первом падении
	$(WEB) pytest -x

# =============================================================================
# Utility
# =============================================================================

.PHONY: db-reset
db-reset: ## Полный сброс БД (drop + up + migrate)
	$(DC) down -v
	$(DC) up -d
	@echo "Ждём готовности БД..."
	@sleep 3
	$(WEB) python manage.py migrate

.PHONY: clean
clean: ## Удалить кэши Python
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
