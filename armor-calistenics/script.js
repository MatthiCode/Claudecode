// Menu plein écran
const burger = document.querySelector('.burger');
const menu = document.getElementById('menu');
function setMenu(open) {
  menu.hidden = !open;
  document.body.classList.toggle('menu-open', open);
  burger.setAttribute('aria-expanded', open);
  burger.querySelector('.burger-label').textContent = open ? 'Fermer' : 'Menu';
  if (open) menu.querySelector('a').focus();
}
burger.addEventListener('click', () => setMenu(menu.hidden));
menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !menu.hidden) { setMenu(false); burger.focus(); }
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
