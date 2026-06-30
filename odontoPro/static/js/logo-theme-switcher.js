(function(){
    'use strict';

    function updateLogoSrc() {
        const logos = document.querySelectorAll('img[src*="logo icon.png"], img[src*="logo-odontohub"], img[alt="OdontoHub"], img[alt*="OdontoHub"]');

        logos.forEach(logo => {
            if (!logo.src.includes('logo-odontohub%20(1)-imagens-3.jpg') && !logo.src.includes('logo-odontohub (1)-imagens-3.jpg')) {
                logo.src = logo.src.replace('logo icon.png', 'logo-odontohub%20(1)-imagens-3.jpg');
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
