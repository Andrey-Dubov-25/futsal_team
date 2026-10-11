"""Management command: синхронизация данных с befutsal.ru.

Использование:

    python manage.py sync_befutsal

Что делает:
    1. Парсит страницу команды на Befutsal.
    2. Создаёт снимок (BefutsalSnapshot) с текущей статистикой.
    3. Обновляет/создаёт турниры (BefutsalTournament) по external_id.
    4. Помечает активные турниры (самый свежий сезон).
    5. Логирует результат.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.league.models import BefutsalSnapshot, BefutsalTournament
from apps.league.parser import BefutsalParseError, parse_club_page


class Command(BaseCommand):
    help = 'Синхронизировать данные с befutsal.ru'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать, что будет сделано, без записи в БД',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write('Загрузка данных с befutsal.ru...')

        # --- Парсинг ---
        try:
            page = parse_club_page()
        except BefutsalParseError as exc:
            self.stderr.write(
                self.style.ERROR(f'Ошибка парсинга: {exc}'),
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Парсинг успешен: {len(page.tournaments)} турниров',
            ),
        )

        if dry_run:
            self._show_dry_run(page)
            return

        # --- Запись в БД ---
        with transaction.atomic():
            snapshot = self._save_snapshot(page)
            stats = self._sync_tournaments(page.tournaments)

        # --- Итог ---
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Синхронизация завершена'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'Снимок создан: {snapshot}')
        self.stdout.write(
            f'Турниров создано: {stats["created"]}, '
            f'обновлено: {stats["updated"]}, '
            f'активных: {stats["active"]}',
        )
        if stats.get('skipped_active'):
            self.stdout.write(
                self.style.WARNING(
                    f'Пропущено (закреплены вручную): '
                    f'{stats["skipped_active"]}',
                ),
            )

    def _save_snapshot(self, page):
        """Сохранить снимок общей статистики."""
        info = page.info

        # Если последний снимок идентичен — не дублируем
        last = BefutsalSnapshot.objects.first()
        if last and self._is_same_snapshot(last, info):
            self.stdout.write(
                'Статистика не изменилась с прошлого снимка, '
                'создание нового не требуется.',
            )
            return last

        snapshot = BefutsalSnapshot.objects.create(
            founded_year=info.founded_year,
            ranking_place=info.ranking_place,
            total_matches=info.total_matches,
            total_won=info.total_won,
            total_drawn=info.total_drawn,
            total_lost=info.total_lost,
            total_goals_scored=info.total_goals_scored,
            total_goals_conceded=info.total_goals_conceded,
        )
        self.stdout.write(f'Создан новый снимок: {snapshot}')
        return snapshot

    @staticmethod
    def _is_same_snapshot(snapshot, info):
        """Проверить, что статистика не изменилась."""
        return (
            snapshot.founded_year == info.founded_year
            and snapshot.ranking_place == info.ranking_place
            and snapshot.total_matches == info.total_matches
            and snapshot.total_won == info.total_won
            and snapshot.total_drawn == info.total_drawn
            and snapshot.total_lost == info.total_lost
            and snapshot.total_goals_scored == info.total_goals_scored
            and snapshot.total_goals_conceded == info.total_goals_conceded
        )

    def _sync_tournaments(self, tournaments):
        """Обновить/создать турниры, отметить активные."""
        created = 0
        updated = 0
        skipped_active = 0

        active_orders = self._detect_active_orders(tournaments)

        for t in tournaments:
            is_active = t.order in active_orders

            # Ищем существующий турнир
            if t.external_id:
                existing = BefutsalTournament.objects.filter(
                    external_id=t.external_id,
                ).first()
                lookup = {'external_id': t.external_id}
            else:
                existing = BefutsalTournament.objects.filter(
                    name=t.name,
                    external_id__isnull=True,
                ).first()
                lookup = {'name': t.name, 'external_id__isnull': True}

            # Определяем, обновлять ли is_active
            if existing and existing.is_pinned:
                # Закреплён — не трогаем is_active
                update_data = self._build_update_data(
                    t,
                    is_active=None,  # None = не трогать
                )
                skipped_active += 1
            else:
                # Обычное обновление, включая is_active
                update_data = self._build_update_data(
                    t,
                    is_active=is_active,
                )

            obj, was_created = BefutsalTournament.objects.update_or_create(
                **lookup,
                defaults=update_data,
            )

            if was_created:
                created += 1
            else:
                updated += 1

        return {
            'created': created,
            'updated': updated,
            'active': len(active_orders),
            'skipped_active': skipped_active,
        }

    @staticmethod
    def _build_update_data(parsed, is_active):
        """Собрать defaults для update_or_create.

        Если is_active=None — поле не включается в обновление.
        """
        data = {
            'name': parsed.name,
            'season': parsed.season,
            'competition': parsed.competition,
            'matches': parsed.matches,
            'won': parsed.won,
            'drawn': parsed.drawn,
            'lost': parsed.lost,
            'goals_scored': parsed.goals_scored,
            'goals_conceded': parsed.goals_conceded,
            'points': parsed.points,
            'percent': parsed.percent,
            'place': parsed.place,
            'order': parsed.order,
        }
        if is_active is not None:
            data['is_active'] = is_active
        return data

    @staticmethod
    def _detect_active_orders(tournaments):
        """Определить order'ы активных турниров.

        Активные = все турниры самого свежего сезона.
        Самый свежий сезон — сезон турнира с наименьшим order.
        """
        if not tournaments:
            return set()

        # Самый свежий сезон — по первому турниру
        latest_season = tournaments[0].season

        # Все турниры этого сезона
        return {t.order for t in tournaments if t.season == latest_season}

    def _show_dry_run(self, page):
        """Показать, что было бы сделано (без записи)."""
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('[DRY RUN] Запись в БД пропущена')
        )
        self.stdout.write('')
        self.stdout.write('Профиль:')
        self.stdout.write(f'  Год: {page.info.founded_year}')
        self.stdout.write(f'  Рейтинг: {page.info.ranking_place}')
        self.stdout.write(f'  Игр: {page.info.total_matches}')
        self.stdout.write('')
        self.stdout.write(f'Турниры ({len(page.tournaments)}):')
        for t in page.tournaments[:5]:
            self.stdout.write(f'  [{t.order:2d}] {t.name[:50]}')
        self.stdout.write(f'  ... и ещё {len(page.tournaments) - 5}')
