"""Константы для тестов.

Отдельно от config/constants.py, потому что тестовые данные
не должны попадать в продовый код.
"""

# --- Аутентификация ---
TEST_PASSWORD = 'testpass123'

# --- Игроки ---
TEST_DEFAULT_NUMBER = 99
TEST_TOTAL_PLAYERS = 3
TEST_GOALS_FORWARD = 2
TEST_ASSISTS_DEFENDER = 1

# --- Матчи ---
TEST_MATCHES_TOTAL = 1
TEST_GOALS_SCORED = 3
TEST_GOALS_CONCEDED = 1
TEST_GOAL_DIFFERENCE = 2
TEST_WIN_RATE = 100.0
TEST_MATCH_EVENTS_COUNT = 3
TEST_EVENT_MINUTE = 15
