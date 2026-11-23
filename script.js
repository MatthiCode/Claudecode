// Barre de progression type "story" liée au scroll
const bar = document.getElementById('progress-bar');
function updateProgress() {
  const max = document.documentElement.scrollHeight - innerHeight;
  bar.style.width = (max > 0 ? (scrollY / max) * 100 : 0) + '%';
}
addEventListener('scroll', updateProgress, { passive: true });
addEventListener('resize', updateProgress);
updateProgress();

// Apparition des éléments au scroll
const items = document.querySelectorAll('.card, .info, .list, .cta .huge, .panel > h2');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  items.forEach((el) => { el.classList.add('reveal'); io.observe(el); });
}
