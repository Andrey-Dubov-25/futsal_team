"""Фикстуры для тестов VK-парсера."""

import pytest


@pytest.fixture
def vk_wall_response():
    """Ответ VK API с несколькими постами.

    Мини-версия реального ответа: посты с фото, видео, репостом.
    """
    return {
        'response': {
            'count': 164,
            'items': [
                {
                    'id': 330,
                    'owner_id': -230450774,
                    'date': 1790171008,
                    'text': (
                        '⚽⚽⚽ Голы за сезон ⚽⚽⚽\n\n'
                        'От самых простых и рабочих...'
                    ),
                    'attachments': [],
                    'copy_history': [
                        {
                            'attachments': [
                                {
                                    'type': 'video',
                                    'video': {
                                        'image': [
                                            {
                                                'width': 320,
                                                'height': 180,
                                                'url': 'https://example.com/small.jpg',
                                            },
                                            {
                                                'width': 1280,
                                                'height': 720,
                                                'url': 'https://example.com/big.jpg',
                                            },
                                        ],
                                    },
                                }
                            ],
                        }
                    ],
                    'likes': {'count': 8},
                    'views': {'count': 136},
                },
                {
                    'id': 329,
                    'owner_id': -230450774,
                    'date': 1789851961,
                    'text': (
                        '📹📹📹 Обзор голов 📹📹📹\n\n'
                        'Лига 4. Второй стыковой матч...'
                    ),
                    'attachments': [
                        {
                            'type': 'video',
                            'video': {
                                'image': [
                                    {
                                        'width': 1280,
                                        'height': 720,
                                        'url': 'https://example.com/video_preview.jpg',
                                    },
                                ],
                            },
                        }
                    ],
                },
                {
                    'id': 312,
                    'owner_id': -230450774,
                    'date': 1789501897,
                    'text': '🏆🏆🏆 Победа 🏆🏆🏆\n\nРазвязка сезона...',
                    'attachments': [
                        {
                            'type': 'photo',
                            'photo': {
                                'sizes': [
                                    {
                                        'width': 72,
                                        'height': 54,
                                        'url': 'https://example.com/photo_s.jpg',
                                    },
                                    {
                                        'width': 2560,
                                        'height': 1920,
                                        'url': 'https://example.com/photo_w.jpg',
                                    },
                                ],
                            },
                        },
                    ],
                },
                {
                    # Пост БЕЗ текста — должен пропускаться
                    'id': 311,
                    'owner_id': -230450774,
                    'date': 1789500000,
                    'text': '',
                    'attachments': [],
                },
            ],
        },
    }


@pytest.fixture
def mock_vk_api(mocker, vk_wall_response):
    """Мок requests.get для VK API."""

    class MockResponse:
        def __init__(self, data):
            self._data = data

        def json(self):
            return self._data

        def raise_for_status(self):
            pass

    return mocker.patch(
        'apps.vk.parser.requests.get',
        return_value=MockResponse(vk_wall_response),
    )
