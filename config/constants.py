"""Числовые константы полей моделей."""

# --- User ---
USER_ROLE_MAX_LENGTH = 10
USER_PHONE_MAX_LENGTH = 20
USER_PASSWORD_MIN_LENGTH = 8

# --- Player ---
PLAYER_FIRST_NAME_MAX_LENGTH = 50
PLAYER_LAST_NAME_MAX_LENGTH = 50
PLAYER_NICKNAME_MAX_LENGTH = 50
PLAYER_POSITION_MAX_LENGTH = 2

# --- Match ---
MATCH_OPPONENT_MAX_LENGTH = 100
MATCH_LOCATION_MAX_LENGTH = 200
MATCH_STATUS_MAX_LENGTH = 3

# --- MatchEvent ---
MATCH_EVENT_TYPE_MAX_LENGTH = 10

# --- NewsPost ---
NEWS_TITLE_MAX_LENGTH = 200
NEWS_SLUG_MAX_LENGTH = 200
NEWS_EXCERPT_MAX_LENGTH = 300
COMMENT_TEXT_MAX_LENGTH = 1000

# --- API ---
API_PAGE_SIZE = 20

# --- JWT ---
JWT_ACCESS_MINUTES = 60
JWT_REFRESH_DAYS = 7

# --- Staff ---
STAFF_ROLE_MAX_LENGTH = 20
STAFF_PHONE_MAX_LENGTH = 20
STAFF_EMAIL_MAX_LENGTH = 254
STAFF_FIRST_NAME_MAX_LENGTH = 50
STAFF_LAST_NAME_MAX_LENGTH = 50

# --- Training ---
TRAINING_TITLE_MAX_LENGTH = 100
TRAINING_LOCATION_MAX_LENGTH = 200
TRAINING_DEFAULT_DURATION_MINUTES = 90

# --- Gallery ---
ALBUM_TITLE_MAX_LENGTH = 200
ALBUM_SLUG_MAX_LENGTH = 200
ALBUM_DESCRIPTION_MAX_LENGTH = 500
PHOTO_CAPTION_MAX_LENGTH = 300

# --- Site ---
SITE_NAME = 'МФК «Восход»'
SITE_DESCRIPTION = (
    'Официальный сайт мини-футбольного клуба «Восход» из Владимира: '
    'расписание матчей, состав команды, статистика игроков, '
    'новости и фотогалерея.'
)
SITE_KEYWORDS = (
    'мини-футбол, МФК Восход, Владимир, футзал, команда, матчи, '
    'статистика, игроки, новости'
)

# --- Пагинация ---
PAGE_SIZE_NEWS = 10
PAGE_SIZE_MATCHES = 10
PAGE_SIZE_GALLERY = 12
PAGE_SIZE_TRAININGS = 10

# --- Befutsal ---
BEFUTSAL_BASE_URL = 'https://befutsal.ru'
BEFUTSAL_CLUB_URL = 'https://befutsal.ru/club.php?t=224668574'
BEFUTSAL_USER_AGENT = 'Mozilla/5.0 (compatible; FutsalTeamBot/1.0)'
BEFUTSAL_REQUEST_TIMEOUT = 10

BEFUTSAL_EXTERNAL_ID_MAX_LENGTH = 50
BEFUTSAL_TOURNAMENT_NAME_MAX_LENGTH = 200
BEFUTSAL_SEASON_MAX_LENGTH = 50
BEFUTSAL_COMPETITION_MAX_LENGTH = 100

# =============================================================================
# О клубе
# =============================================================================

"""Слоган команды — короткая фраза для hero-блока."""
SITE_SLOGAN = 'От простых дворовых побед до серьёзных высот'

"""Короткое описание — для hero и meta."""
SITE_SHORT_DESCRIPTION = (
    'Мини-футбольный клуб из Владимира. Играем в городской '
    'любительской лиге с 2021 года.'
)

"""История клуба — текст для страницы «О клубе».

Можно редактировать вручную. Поддерживаются абзацы через
пустую строку.
"""
SITE_HISTORY = """
История МФК «Восход» начинается в 2021 году. Команда собралась
из друзей и знакомых, которые хотели играть в футбол на более
серьёзном уровне, чем дворовые матчи. Первый сезон во 4-й лиге
городской федерации футбола дался тяжело — команда заняла 17-е
место из 18 возможных.

Несмотря на неудачный старт, команда продолжила выступления.
Постепенно состав укреплялся, приходили новые игроки, оттачивалась
тактика. Результаты росли из года в год: сначала попадание в
середину таблицы, затем борьба за топ-5, а в сезоне «Лето 2026»
команда впервые в своей истории стала **чемпионом 4-й лиги
в своей зоне**.

Сейчас МФК «Восход» — стабильный участник городских турниров
по мини-футболу, с постоянным составом, болельщиками и
тренерским штабом. Команда продолжает развиваться и ставит
новые цели: выход в 3-ю лигу, победы в кубках, привлечение
молодых игроков.
""".strip()

"""Контакты команды."""
SITE_CONTACT_PHONE = '+7 (910) 092-67-61'
SITE_CONTACT_EMAIL = 'voshod@example.com'
SITE_CONTACT_VK = 'https://vk.ru/voshodchane'
SITE_CONTACT_TELEGRAM = ''  # если нет — оставить пустым

"""Город команды."""
SITE_CITY = 'Владимир'

# --- ВКонтакте ---
VK_API_BASE_URL = 'https://api.vk.com/method'
VK_API_VERSION = '5.199'
VK_GROUP_SCREEN_NAME = 'voshodchane'
VK_GROUP_OWNER_ID = -230450774
VK_REQUEST_TIMEOUT = 10
VK_POSTS_COUNT = 30

VK_EXTERNAL_ID_MAX_LENGTH = 50
VK_POST_LINK = 'https://vk.com/wall{owner_id}_{post_id}'

VK_TITLE_MAX_LENGTH = 100
