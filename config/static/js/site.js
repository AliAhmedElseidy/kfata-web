(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced || document.body.dataset.motion !== 'on') return;
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
    }), { threshold: .08 });
    document.querySelectorAll('.reveal').forEach(element => observer.observe(element));
    document.body.classList.add('motion-ready');
    // Fail open even if observers cannot deliver callbacks.
    setTimeout(() => document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible')), 5000);
  }
  try {
    if (document.body.dataset.opening === 'on' && !sessionStorage.getItem('kfata-intro')) {
      sessionStorage.setItem('kfata-intro', '1');
      const opening = document.createElement('div');
      opening.className = 'opening-mark'; opening.setAttribute('aria-hidden', 'true');
      const mark = document.createElement('span'); mark.textContent = 'KFΛTA'; opening.append(mark);
      document.body.append(opening); setTimeout(() => opening.remove(), 1500);
    }
  } catch (_) { /* Storage access must never block the site. */ }
})();
