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
            if (themeToggle) themeToggle.textContent = 'Tema escuro';
        } else {
            document.body.classList.remove('theme-dark');
            if (themeToggle) themeToggle.textContent = 'Tema claro';
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

    const previewCards = Array.from(document.querySelectorAll('.clinic-cards-preview .clinic-card'));

    if (previewCards.length) {
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
    }

    const featuredCards = Array.from(document.querySelectorAll('.floating-clinic-cards .clinic-card'));
    const featuredScroll = document.querySelector('.floating-cards-scroll');

    if (featuredCards.length > 1 && featuredScroll) {
        let featuredIndex = 0;

        const rotateFeaturedClinics = () => {
            const firstCard = featuredScroll.firstElementChild;
            if (!firstCard) return;
            featuredScroll.appendChild(firstCard);
        };

        setInterval(rotateFeaturedClinics, 5000);
    }

    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Abrir menu');
        navToggle.innerHTML = '<i class="fa-solid fa-bars"></i>';

        navToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = navLinks.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', String(isOpen));
            navToggle.setAttribute('aria-label', isOpen ? 'Fechar menu' : 'Abrir menu');
            navToggle.innerHTML = isOpen ? '<i class="fa-solid fa-xmark"></i>' : '<i class="fa-solid fa-bars"></i>';
        });

        document.addEventListener('click', (event) => {
            if (navLinks.classList.contains('open') && !navLinks.contains(event.target) && !navToggle.contains(event.target)) {
                navLinks.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.setAttribute('aria-label', 'Abrir menu');
                navToggle.innerHTML = '<i class="fa-solid fa-bars"></i>';
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth > 900 && navLinks.classList.contains('open')) {
                navLinks.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.setAttribute('aria-label', 'Abrir menu');
                navToggle.innerHTML = '<i class="fa-solid fa-bars"></i>';
            }
        });
    }
});
