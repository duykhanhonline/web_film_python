import { initRowScroll } from './row-scroll.js';
import { initMyList } from './my-list.js';
import { initAds } from './ads.js';

function initHeader() {
  const header = document.querySelector('[data-site-header]');
  if (!header) return;
  const overlay = document.body.dataset.header === 'overlay';
  const update = () => header.toggleAttribute('data-scrolled', !overlay || scrollY > 8);
  update();
  if (overlay) addEventListener('scroll', update, { passive: true });
}

function initDropdowns() {
  const closeAll = (except) => {
    document.querySelectorAll('[data-dropdown][aria-expanded="true"]').forEach((btn) => {
      if (btn === except) return;
      btn.setAttribute('aria-expanded', 'false');
      document.getElementById(btn.getAttribute('aria-controls')).hidden = true;
    });
  };

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-dropdown]');
    if (!btn) {
      if (!e.target.closest('[data-dropdown] + *')) closeAll();
      return;
    }
    const open = btn.getAttribute('aria-expanded') !== 'true';
    closeAll(btn);
    btn.setAttribute('aria-expanded', String(open));
    document.getElementById(btn.getAttribute('aria-controls')).hidden = !open;
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const open = document.querySelector('[data-dropdown][aria-expanded="true"]');
    if (!open) return;
    closeAll();
    open.focus();
  });
}

initHeader();
initDropdowns();
initRowScroll();
initMyList();
initAds();
