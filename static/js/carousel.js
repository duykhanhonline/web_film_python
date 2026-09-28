const AUTOPLAY_MS = 7000;
// The backdrop image shows this long before the trailer fades in
const TRAILER_DELAY_MS = 3000;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const desktop = matchMedia('(min-width: 1024px) and (pointer: fine)');

// Trailers play only on desktop, on a fast connection, without reduced motion
function trailersAllowed() {
  if (reducedMotion.matches || !desktop.matches) return false;
  const conn = navigator.connection;
  return !conn || (!conn.saveData && (!conn.effectiveType || conn.effectiveType === '4g'));
}

// Swaps data-src/data-srcset into real attributes so offscreen slides load on demand.
// Trailers are skipped: they load only when they are about to play.
function hydrate(slide) {
  slide?.querySelectorAll('img[data-src], img[data-srcset], source[data-srcset]').forEach((el) => {
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
  let trailer = null; // the active slide's <video> (waiting or playing), if any
  let trailerTimer = null;

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

  function setTrailerButton(slide, playing) {
    const btn = slide?.querySelector('[data-trailer-play]');
    if (!btn) return;
    btn.setAttribute('aria-pressed', String(playing));
    btn.querySelector('[data-trailer-label]').textContent = playing ? 'Dừng trailer' : 'Xem trailer';
  }

  function stopTrailer() {
    clearTimeout(trailerTimer);
    if (!trailer) return;
    trailer.pause();
    trailer.removeAttribute('data-playing');
    delete trailer.dataset.manual;
    setTrailerButton(trailer.closest('[data-slide]'), false);
    trailer = null;
  }

  // Mobile/tablet: the user taps "Xem trailer". Plays with sound; tap again to stop.
  function toggleManualTrailer() {
    const video = slides[index].querySelector('video[data-trailer]');
    if (!video) return;
    if (trailer === video) {
      stopTrailer();
      schedule();
      return;
    }
    stopTrailer();
    clearTimeout(timer);
    if (!video.src) video.src = video.dataset.src;
    video.muted = false;
    video.currentTime = 0;
    video.dataset.manual = '';
    trailer = video;
    setTrailerButton(slides[index], true);
    // play() runs inside the tap, so mobile browsers allow sound
    video.play().then(
      () => { if (trailer === video) video.setAttribute('data-playing', ''); },
      () => { if (trailer === video) { stopTrailer(); schedule(); } },
    );
  }

  // Shows the backdrop first, then plays the active slide's trailer muted.
  // Returns false when there is no trailer or it may not play.
  function playTrailer() {
    const video = slides[index].querySelector('video[data-trailer]');
    if (!video || userPaused || document.hidden || !trailersAllowed()) return false;
    if (!video.src) {
      video.preload = 'auto'; // buffer while the backdrop is showing
      video.src = video.dataset.src;
    }
    video.muted = true;
    video.currentTime = 0;
    trailer = video;
    clearTimeout(trailerTimer);
    trailerTimer = setTimeout(() => {
      if (trailer !== video) return;
      video.play().then(
        () => { if (trailer === video) video.setAttribute('data-playing', ''); },
        () => { if (trailer === video) { trailer = null; schedule(); } },
      );
    }, TRAILER_DELAY_MS);
    return true;
  }

  slides.forEach((slide) => {
    const video = slide.querySelector('video[data-trailer]');
    if (!video) return;
    video.addEventListener('ended', () => {
      if (trailer !== video) return;
      const manual = 'manual' in video.dataset;
      stopTrailer();
      // A tapped trailer returns to the image; an autoplayed one moves to the next slide
      if (manual || userPaused || hoverPaused) schedule();
      else show(index + 1);
    });
    video.addEventListener('error', () => {
      if (trailer !== video) return;
      stopTrailer();
      schedule();
    });
  });

  function show(i) {
    stopTrailer();
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
    if (!playTrailer()) schedule();
    else clearTimeout(timer);
  }

  function schedule() {
    clearTimeout(timer);
    // A playing trailer moves to the next slide itself when it ends
    if (trailer || userPaused || hoverPaused || document.hidden || count < 2) return;
    timer = setTimeout(() => show(index + 1), AUTOPLAY_MS);
  }

  function syncToggle() {
    if (!toggle) return;
    toggle.setAttribute('aria-label', userPaused ? 'Tiếp tục tự chuyển' : 'Tạm dừng tự chuyển');
    toggle.setAttribute('aria-pressed', String(userPaused));
  }

  root.addEventListener('click', (e) => {
    if (e.target.closest('[data-trailer-play]')) toggleManualTrailer();
  });
  root.querySelector('[data-carousel-prev]')?.addEventListener('click', () => show(index - 1));
  root.querySelector('[data-carousel-next]')?.addEventListener('click', () => show(index + 1));
  toggle?.addEventListener('click', () => {
    userPaused = !userPaused;
    syncToggle();
    if (userPaused) stopTrailer();
    else if (playTrailer()) return;
    schedule();
  });

  // Pause while the user is reading or interacting
  const pause = (on) => { hoverPaused = on; schedule(); };
  root.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') pause(true); });
  root.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') pause(false); });
  root.addEventListener('focusin', () => pause(true));
  root.addEventListener('focusout', (e) => { if (!root.contains(e.relatedTarget)) pause(false); });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopTrailer();
    else if (playTrailer()) return;
    schedule();
  });

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

document.querySelectorAll('[data-carousel]').forEach(initCarousel);
