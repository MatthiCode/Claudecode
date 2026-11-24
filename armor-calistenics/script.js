// Menu mobile
const burger = document.querySelector('.burger');
const menu = document.getElementById('menu');
burger.addEventListener('click', () => {
  const open = menu.classList.toggle('open');
  burger.setAttribute('aria-expanded', open);
  burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
});
menu.addEventListener('click', e => {
  if (e.target.closest('a')) {
    menu.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
  }
});

// Formulaire : ouvre le client mail avec le message prérempli
const form = document.getElementById('form');
const err = document.getElementById('err');
form.addEventListener('submit', e => {
  e.preventDefault();
  const nom = form.nom.value.trim();
  const msg = form.msg.value.trim();
  if (!nom || !msg) { err.hidden = false; return; }
  err.hidden = true;
  const body = `Prénom : ${nom}\nNiveau : ${form.niveau.value}\n\n${msg}`;
  location.href = 'mailto:armorcalistenics@gmail.com?subject=' +
    encodeURIComponent('Rejoindre Armor Calistenics') + '&body=' + encodeURIComponent(body);
});
