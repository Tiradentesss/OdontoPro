document.addEventListener('DOMContentLoaded', function(){
    const dl = document.getElementById('download-desktop');
    if (dl) dl.addEventListener('click', (e)=>{ e.preventDefault(); const href = dl.getAttribute('href'); if (href) window.location.href = href; });

    const appstore = document.getElementById('link-appstore');
    const playstore = document.getElementById('link-playstore');
    if (appstore) appstore.addEventListener('click',(e)=>{ e.preventDefault(); const href = appstore.getAttribute('href'); if (href) window.location.href = href; });
    if (playstore) playstore.addEventListener('click',(e)=>{ e.preventDefault(); const href = playstore.getAttribute('href'); if (href) window.location.href = href; });

    // Theme toggle: persist choice to localStorage
    const themeToggle = document.getElementById('theme-toggle');
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.body.classList.add('theme-dark');
            if (themeToggle) themeToggle.textContent = '☀️';
        } else {
            document.body.classList.remove('theme-dark');
            if (themeToggle) themeToggle.textContent = '🌙';
        }
    };

    // Initialize theme from localStorage (default light)
    const stored = localStorage.getItem('odontopro_theme') || 'light';
    applyTheme(stored);

    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            const current = document.body.classList.contains('theme-dark') ? 'dark' : 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            localStorage.setItem('odontopro_theme', next);
            applyTheme(next);
        });
    }

    const previewCards = Array.from(document.querySelectorAll('.clinic-card'));
    const premiumCards = previewCards.filter(card => parseFloat(card.dataset.rating) >= 4.5);

    if (premiumCards.length > 2) {
        let currentIndex = 0;
        const visibleCount = 2;

        const renderPreview = () => {
            previewCards.forEach(card => card.classList.remove('is-active'));

            for (let offset = 0; offset < visibleCount; offset++) {
                const index = (currentIndex + offset) % premiumCards.length;
                premiumCards[index].classList.add('is-active');
            }

            currentIndex = (currentIndex + 1) % premiumCards.length;
        };

        renderPreview();
        setInterval(renderPreview, 5000);
    } else {
        previewCards.forEach(card => card.classList.add('is-active'));
    }
});
