/* Лайтбокс для галереи */

(function () {
    'use strict';

    const grid = document.getElementById('photos-grid');
    const lightbox = document.getElementById('lightbox');
    if (!grid || !lightbox) return;

    const items = Array.from(grid.querySelectorAll('.photo-item'));
    const image = lightbox.querySelector('.lightbox__image');
    const caption = lightbox.querySelector('.lightbox__caption');
    const btnClose = lightbox.querySelector('.lightbox__close');
    const btnPrev = lightbox.querySelector('.lightbox__prev');
    const btnNext = lightbox.querySelector('.lightbox__next');

    let currentIndex = 0;

    function show(index) {
        if (index < 0) index = items.length - 1;
        if (index >= items.length) index = 0;

        currentIndex = index;
        const item = items[index];
        const href = item.getAttribute('href');
        const alt = item.querySelector('img').getAttribute('alt') || '';
        const text = item.getAttribute('data-photo-caption') || '';

        image.src = href;
        image.alt = alt;
        caption.textContent = text;
        caption.style.display = text ? 'block' : 'none';

        lightbox.hidden = false;
        document.body.style.overflow = 'hidden';
    }

    function close() {
        lightbox.hidden = true;
        image.src = '';
        document.body.style.overflow = '';
    }

    items.forEach((item, i) => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            show(i);
        });
    });

    btnClose.addEventListener('click', close);
    btnPrev.addEventListener('click', () => show(currentIndex - 1));
    btnNext.addEventListener('click', () => show(currentIndex + 1));

    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) close();
    });

    document.addEventListener('keydown', (e) => {
        if (lightbox.hidden) return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') show(currentIndex - 1);
        if (e.key === 'ArrowRight') show(currentIndex + 1);
    });
})();
