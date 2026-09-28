const AUTOPLAY_MS = 7000;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

// Swaps data-src/data-srcset into real attributes so offscreen slides load on demand
function hydrate(slide) {
  slide?.querySelectorAll('[data-src], [data-srcset]').forEach((el) => {
    if (el.dataset.srcset) el.srcset = el.dataset.srcset;
    if (el.dataset.src) el.src = el.dataset.src;
    delete el.dataset.src;
    delete el.dataset.srcset;
  });
}

/*
  <section data-carousel>
    <div data-carousel-track> <div data-slide>…</div> … </div>
    <button data-carousel-prev> <button data-carousel-next>
    <div data-carousel-dots></div> <button data-carousel-toggle>
*/
export function initCarousel(root) {
  const slides = [...root.querySelectorAll('[data-slide]')];
  if (!slides.length) return;

  const dotsBox = root.querySelector('[data-carousel-dots]');
  const toggle = root.querySelector('[data-carousel-toggle]');
  const count = slides.length;
  let index = 0;
  let timer = null;
  let userPaused = reducedMotion.matches;
  let hoverPaused = false;

  const dots = slides.map((_, i) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'group flex size-11 items-center justify-center rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand';
    dot.setAttribute('aria-label', `Chuyển đến slide ${i + 1}`);
    dot.innerHTML = '<span class="h-1.5 w-4 rounded-full bg-text/40 transition-all group-aria-[current=true]:w-6 group-aria-[current=true]:bg-text"></span>';
    dot.addEventListener('click', () => show(i));
    dotsBox?.append(dot);
    return dot;
  });

  function show(i) {
    index = (i + count) % count;
    slides.forEach((slide, n) => {
      const active = n === index;
      slide.toggleAttribute('data-active', active);
      slide.inert = !active;
      slide.setAttribute('aria-hidden', String(!active));
      dots[n].setAttribute('aria-current', String(active));
    });
    hydrate(slides[index]);
    hydrate(slides[(index + 1) % count]);
    schedule();
  }

  function schedule() {
    clearTimeout(timer);
    if (userPaused || hoverPaused || document.hidden || count < 2) return;
    timer = setTimeout(() => show(index + 1), AUTOPLAY_MS);
  }

  function syncToggle() {
    if (!toggle) return;
    toggle.setAttribute('aria-label', userPaused ? 'Tiếp tục tự chuyển' : 'Tạm dừng tự chuyển');
    toggle.setAttribute('aria-pressed', String(userPaused));
  }

  root.querySelector('[data-carousel-prev]')?.addEventListener('click', () => show(index - 1));
  root.querySelector('[data-carousel-next]')?.addEventListener('click', () => show(index + 1));
  toggle?.addEventListener('click', () => {
    userPaused = !userPaused;
    syncToggle();
    schedule();
  });

  // Pause while the user is reading or interacting
  const pause = (on) => { hoverPaused = on; schedule(); };
  root.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') pause(true); });
  root.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') pause(false); });
  root.addEventListener('focusin', () => pause(true));
  root.addEventListener('focusout', (e) => { if (!root.contains(e.relatedTarget)) pause(false); });
  document.addEventListener('visibilitychange', schedule);

  root.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(index - 1);
    else if (e.key === 'ArrowRight') show(index + 1);
    else return;
    e.preventDefault();
  });

  // Swipe on touch screens
  let startX = null;
  root.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') startX = e.clientX; });
  root.addEventListener('pointerup', (e) => {
    if (startX === null) return;
    const dx = e.clientX - startX;
    startX = null;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
  });

  syncToggle();
  show(0);
}
