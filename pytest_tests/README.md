# Тесты

Тесты проекта на **pytest** + **pytest-django** + **factory-boy**.

## Быстрый старт

```bash
# Через make
make test            # все тесты
make test-fast       # стоп на первом падении
make test-cov        # с покрытием + HTML-отчёт

# Напрямую
docker compose exec web pytest
docker compose exec web pytest pytest_tests/players/
docker compose exec web pytest pytest_tests/api/test_stats_endpoints.py
docker compose exec web pytest -k "auth"
docker compose exec web pytest -x
docker compose exec web pytest -v
docker compose exec web pytest --lf
docker compose exec web pytest --pdb
