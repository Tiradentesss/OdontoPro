(function(){
    'use strict';

    function isDarkMode() {
        return document.body.classList.contains('theme-dark') || document.body.classList.contains('dark');
    }

    function updateLogoSrc() {
        const logos = document.querySelectorAll('img[src*="Logo Transparente 1.png"], img[src*="logo icon.png"], img[src*="logo-odontohub"], img[alt="OdontoHub"], img[alt*="OdontoHub"], .home-logo');

        logos.forEach(logo => {
            const currentSrc = logo.getAttribute('data-original-src') || logo.src;
            if (!logo.hasAttribute('data-original-src')) {
                logo.setAttribute('data-original-src', currentSrc);
            }

            if (logo.hasAttribute('data-light-src') && logo.hasAttribute('data-dark-src')) {
                logo.src = isDarkMode() ? logo.getAttribute('data-dark-src') : logo.getAttribute('data-light-src');
                return;
            }

            if (isDarkMode()) {
                if (!logo.src.includes('Logo%20Transparente%20white.png') && !logo.src.includes('Logo Transparente white.png')) {
                    logo.src = logo.src.replace('Logo%20Transparente%201.png', 'Logo%20Transparente%20white.png');
                    logo.src = logo.src.replace('Logo Transparente 1.png', 'Logo Transparente white.png');
                    logo.src = logo.src.replace('logo icon.png', 'Logo%20Transparente%20white.png');
                    logo.src = logo.src.replace('logo-odontohub%20(1)-imagens-3.jpg', 'Logo%20Transparente%20white.png');
                    logo.src = logo.src.replace('logo-odontohub (1)-imagens-3.jpg', 'Logo%20Transparente%20white.png');
                }
            } else {
                logo.src = logo.getAttribute('data-original-src');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', updateLogoSrc);

    const observer = new MutationObserver(() => {
        updateLogoSrc();
    });

    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
})();
