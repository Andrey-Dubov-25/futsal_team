"""Фабрики моделей для тестов."""

import factory
from django.utils import timezone

from apps.accounts.models import User
from apps.matches.models import Match, MatchEvent
from apps.news.models import NewsPost
from apps.players.models import Player
from pytest_tests import constants as c


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика пользователя."""

    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(
        lambda o: f'{o.username}@example.com',
    )
    role = User.Role.FAN
    password = factory.PostGenerationMethodCall(
        'set_password',
        c.TEST_PASSWORD,
    )


class PlayerFactory(factory.django.DjangoModelFactory):
    """Фабрика игрока."""

    class Meta:
        model = Player
        django_get_or_create = ('number',)

    first_name = factory.Faker('first_name', locale='ru_RU')
    last_name = factory.Faker('last_name', locale='ru_RU')
    number = factory.Sequence(lambda n: n + 1)
    position = Player.Position.FORWARD
    is_active = True


class MatchFactory(factory.django.DjangoModelFactory):
    """Фабрика матча."""

    class Meta:
        model = Match

    opponent = factory.Faker('company', locale='ru_RU')
    date = factory.LazyFunction(timezone.now)
    location = 'Дом'
    is_home = True
    status = Match.Status.SCHEDULED
    our_score = None
    opponent_score = None


class FinishedMatchFactory(MatchFactory):
    """Фабрика завершённого матча со счётом."""

    status = Match.Status.FINISHED
    our_score = c.TEST_GOALS_SCORED
    opponent_score = c.TEST_GOALS_CONCEDED


class MatchEventFactory(factory.django.DjangoModelFactory):
    """Фабрика события матча."""

    class Meta:
        model = MatchEvent

    match = factory.SubFactory(MatchFactory)
    player = factory.SubFactory(PlayerFactory)
    event_type = MatchEvent.EventType.GOAL
    minute = c.TEST_EVENT_MINUTE


class NewsPostFactory(factory.django.DjangoModelFactory):
    """Фабрика новости."""

    class Meta:
        model = NewsPost

    title = factory.Faker('sentence', locale='ru_RU')
    excerpt = factory.Faker('sentence', locale='ru_RU')
    content = factory.Faker('paragraph', locale='ru_RU')
    is_published = True
