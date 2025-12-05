// perfil_carousel.js
document.addEventListener('DOMContentLoaded', function() {
    const diasCards = document.querySelector('.dias-cards');
    if (!diasCards) return;
  
    // criar botões se ainda não existirem
    function createArrow(className, html) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'carousel-arrow ' + className;
      btn.innerHTML = html;
      btn.setAttribute('aria-hidden', 'true');
      return btn;
    }
  
    const prev = createArrow('carousel-prev', '&#9664;'); // ◄
    const next = createArrow('carousel-next', '&#9654;'); // ►
  
    // coloca os botões no wrapper (pai de dias-cards)
    const wrapper = diasCards.parentElement;
    wrapper.classList.add('dias-wrapper');
    // evita duplicar
    if (!wrapper.querySelector('.carousel-prev')) wrapper.appendChild(prev);
    if (!wrapper.querySelector('.carousel-next')) wrapper.appendChild(next);
  
    // scroll amount: um card + gap (aprox)
    function cardWidth() {
      const card = diasCards.querySelector('.dia-card');
      if (!card) return diasCards.clientWidth * 0.8;
      const style = getComputedStyle(diasCards);
      const gap = parseFloat(style.gap || 15);
      return card.getBoundingClientRect().width + gap;
    }
  
    prev.addEventListener('click', () => {
      diasCards.scrollBy({ left: -cardWidth(), behavior: 'smooth' });
    });
    next.addEventListener('click', () => {
      diasCards.scrollBy({ left: cardWidth(), behavior: 'smooth' });
    });
  
    // escondendo setas quando não necessário
    function updateArrows() {
      if (diasCards.scrollWidth <= diasCards.clientWidth + 4) {
        prev.style.display = 'none';
        next.style.display = 'none';
      } else {
        prev.style.display = 'flex';
        next.style.display = 'flex';
      }
    }
    updateArrows();
    window.addEventListener('resize', updateArrows);
  });

document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector(".dias-cards");
    let isDown = false;
    let startX;
    let scrollLeft;

    // Mouse
    container.addEventListener("mousedown", (e) => {
        isDown = true;
        container.classList.add("active");
        startX = e.pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
    });

    container.addEventListener("mouseleave", () => {
        isDown = false;
    });

    container.addEventListener("mouseup", () => {
        isDown = false;
    });

    container.addEventListener("mousemove", (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - container.offsetLeft;
        const walk = (x - startX) * 1.2;
        container.scrollLeft = scrollLeft - walk;
    });

    // Touch (celular)
    container.addEventListener("touchstart", (e) => {
        isDown = true;
        startX = e.touches[0].pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
    });

    container.addEventListener("touchend", () => {
        isDown = false;
    });

    container.addEventListener("touchmove", (e) => {
        if (!isDown) return;
        const x = e.touches[0].pageX - container.offsetLeft;
        const walk = (x - startX) * 1.2;
        container.scrollLeft = scrollLeft - walk;
    });
});

