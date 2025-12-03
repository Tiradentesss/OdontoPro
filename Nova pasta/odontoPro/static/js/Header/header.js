// ================================
// HEADER FUNCIONAL
// ================================

const notifBtn = document.getElementById('notifBtn');
const notifMenu = document.getElementById('notifMenu');

const userBtn = document.getElementById('userBtn');
const userMenu = document.getElementById('userMenu');

const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const mobileNotifBtn = document.getElementById('mobileNotifBtn');

// Toggle desktop menus
notifBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    notifMenu.classList.toggle('active');
    userMenu.classList.remove('active');
});

userBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    userMenu.classList.toggle('active');
    notifMenu.classList.remove('active');
});

// Toggle mobile menu
hamburger?.addEventListener('click', (e) => {
    e.stopPropagation();
    mobileMenu.classList.toggle('active');
});

// Clique no botão de notificações mobile
mobileNotifBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    alert('Abrir notificações (mobile)');
});

// Fecha menus ao clicar fora
document.addEventListener('click', () => {
    notifMenu.classList.remove('active');
    userMenu.classList.remove('active');
    mobileMenu.classList.remove('active');
});
