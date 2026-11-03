(() => {
  // Local lab diagnostics only: no analytics, cookies or network transmission.
  // These attributes allow QA to inspect actual render timing in this browser.
  if ('PerformanceObserver' in window) {
    try {
      new PerformanceObserver(list => {
        const entries = list.getEntries();
        document.documentElement.dataset.lcpMs = Math.round(entries[entries.length - 1].startTime);
      }).observe({type:'largest-contentful-paint', buffered:true});
      let maximum = 0, total = 0, start = 0, previous = 0;
      new PerformanceObserver(list => list.getEntries().forEach(entry => {
        if (entry.hadRecentInput) return;
        if (entry.startTime - previous > 1000 || entry.startTime - start > 5000) {
          start = entry.startTime; total = 0;
        }
        total += entry.value; previous = entry.startTime; maximum = Math.max(maximum,total);
        document.documentElement.dataset.cls = maximum.toFixed(4);
      })).observe({type:'layout-shift',buffered:true});
      let longest = 0;
      new PerformanceObserver(list => list.getEntries().forEach(entry => {
        if (entry.interactionId) {
          longest = Math.max(longest,entry.duration);
          document.documentElement.dataset.maxInteractionMs = longest;
        }
      })).observe({type:'event',buffered:true,durationThreshold:16});
    } catch (_) { /* Unsupported metrics do not affect content. */ }
  }
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
      const original = document.querySelector('.brand img');
      const mark = original ? original.cloneNode(true) : document.createElement('span');
      if (!original) mark.textContent = 'KFΛTA';
      opening.append(mark);
      document.body.append(opening); setTimeout(() => opening.remove(), 1500);
    }
  } catch (_) { /* Storage access must never block the site. */ }
})();
