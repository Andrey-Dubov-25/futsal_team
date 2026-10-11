"""Расширенный тестовый парсер befutsal.ru."""

import re

import requests
from bs4 import BeautifulSoup


URL = 'https://befutsal.ru/club.php?t=224668574'

response = requests.get(
    URL,
    timeout=10,
    headers={
        'User-Agent': 'Mozilla/5.0 (compatible; FutsalTeamBot/1.0)',
    },
)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

print('=' * 70)
print('ТАБЛИЦА ВЫСТУПЛЕНИЙ — подробно')
print('=' * 70)

tables = soup.find_all('table')
if tables:
    table = tables[0]
    for i, row in enumerate(table.find_all('tr')):
        cells = row.find_all(['td', 'th'])
        cell_texts = [c.get_text(strip=True) for c in cells]
        print(f'Строка {i:2d} ({len(cells)} ячеек): {cell_texts}')

print()
print('=' * 70)
print('ПОИСК БЛОКА «ПРОФИЛЬ КЛУБА»')
print('=' * 70)

# Ищем слово "Основана" и его окружение
page_text = soup.get_text()
match = re.search(r'Основана[:\s]*(\d{4})', page_text)
if match:
    print(f'Год основания: {match.group(1)}')

# Ищем рейтинг
match = re.search(r'(\d+)\s*лучшее место', page_text, re.IGNORECASE)
if match:
    print(f'Место в рейтинге: {match.group(1)}')

# Общая статистика — ищем числа 205, 99, 25, 81
match = re.search(
    r'Игр\s*(\d+).*?Побед\s*(\d+).*?Ничьих\s*(\d+).*?Поражений\s*(\d+)',
    page_text,
    re.DOTALL,
)
if match:
    print(
        f'Игр: {match.group(1)}, Побед: {match.group(2)}, '
        f'Ничьих: {match.group(3)}, Поражений: {match.group(4)}'
    )

match = re.search(
    r'Забито\s*(\d+).*?Пропущено\s*(\d+)',
    page_text,
    re.DOTALL,
)
if match:
    print(f'Забито: {match.group(1)}, Пропущено: {match.group(2)}')

print()
print('=' * 70)
print('HTML-СТРУКТУРА БЛОКА «ПРОФИЛЬ КЛУБА»')
print('=' * 70)

# Найти все div'ы с текстом "Основана"
for el in soup.find_all(string=re.compile('Основана')):
    parent = el.parent
    print(
        f'\nНайден родитель: <{parent.name} class="{parent.get("class", [])}">'
    )
    # Показать 3 уровня вверх
    for _ in range(3):
        parent = parent.parent
        if not parent:
            break
        text = parent.get_text(strip=True)[:300]
        print(f'  ↑ <{parent.name} class="{parent.get("class", [])}">')
        print(f'     {text}')

print()
print('=' * 70)
print('HTML-СТРУКТУРА БЛОКА ОБЩЕЙ СТАТИСТИКИ')
print('=' * 70)

for el in soup.find_all(string=re.compile('Игр')):
    parent = el.parent
    # Найти контейнер
    container = parent.find_parent(['div', 'section', 'table'])
    if container:
        print(
            f'\nНайден контейнер: <{container.name} '
            f'class="{container.get("class", [])}">'
        )
        text = container.get_text(strip=True, separator=' | ')[:400]
        print(f'   {text}')

print()
print('=' * 70)
print('ЧТО ВНУТРИ ЯЧЕЕК ТАБЛИЦЫ (HTML)')
print('=' * 70)

if tables:
    table = tables[0]
    rows = table.find_all('tr')
    if len(rows) > 1:
        row = rows[1]  # Первая строка данных
        print('\nHTML первой строки данных:')
        print(row.prettify()[:2000])
