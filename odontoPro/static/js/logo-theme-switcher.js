(function(){
    'use strict';

    function updateLogoSrc() {
        const isDarkMode = document.body.classList.contains('theme-dark');
        const logos = document.querySelectorAll('img[src*="logo icon.png"], img[alt="OdontoPlace"], img[alt*="OdontoPlace"]');
        
        logos.forEach(logo => {
            if (isDarkMode) {
                logo.src = logo.src.replace('logo icon.png', 'logo-dark.png');
            } else {
                logo.src = logo.src.replace('logo-dark.png', 'logo icon.png');
            }
        });
    }

    // Initial update on page load
    document.addEventListener('DOMContentLoaded', updateLogoSrc);

    // Watch for theme changes (observe mutations to body class)
    const observer = new MutationObserver(() => {
        updateLogoSrc();
    });

    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
})();
