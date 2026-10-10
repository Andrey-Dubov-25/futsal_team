/* Переключение светлой/тёмной темы */

(function () {
    'use strict';

    const STORAGE_KEY = 'theme';
    const root = document.documentElement;

    function getPreferredTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'light' || saved === 'dark') return saved;

        // По умолчанию — светлая
        return 'light';
    }

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);

        // Обновляем иконку на кнопке
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.textContent = theme === 'dark' ? '☀️' : '🌙';
            btn.setAttribute(
                'aria-label',
                theme === 'dark' ? 'Светлая тема' : 'Тёмная тема',
            );
        }
    }

    function toggleTheme() {
        const current = root.getAttribute('data-theme') || 'light';
        applyTheme(current === 'dark' ? 'light' : 'dark');
    }

    // Применяем тему сразу (до отрисовки страницы)
    applyTheme(getPreferredTheme());

    // Навешиваем обработчик после загрузки DOM
    document.addEventListener('DOMContentLoaded', function () {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.addEventListener('click', toggleTheme);
        }
    });
})();
