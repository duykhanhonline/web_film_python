import { includePartials } from './include.js';
import { mountAds } from './ads.js';
import { initRowScroll, createRow, refreshArrows } from './row-scroll.js';
import { createCard } from './card.js';
import { getMovies } from './data.js';

// Dev helper: ?user=vip or ?user=free overrides <body data-user>
function applyUserOverride() {
  const user = new URLSearchParams(location.search).get('user');
  if (user === 'vip' || user === 'free') document.body.dataset.user = user;
}

function initHeader() {
  const header = document.querySelector('[data-site-header]');
  if (!header) return;
  const overlay = document.body.dataset.header === 'overlay';
  const update = () => header.toggleAttribute('data-scrolled', !overlay || scrollY > 8);
  update();
  if (overlay) addEventListener('scroll', update, { passive: true });
}

function markActiveNav() {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('[data-nav]').forEach((link) => {
    const target = link.getAttribute('href').split('?')[0];
    if (target === page) link.setAttribute('aria-current', 'page');
  });
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

// <div data-movie-row data-title="..." data-country="Hàn Quốc" data-type="bo" data-genre="..."
//      data-sort="new" data-see-all="...">
async function mountMovieRows() {
  const slots = [...document.querySelectorAll('[data-movie-row]')];
  if (!slots.length) return;
  const movies = await getMovies();

  await Promise.all(slots.map(async (slot) => {
    const { title, country, type, genre, sort, seeAll, limit } = slot.dataset;
    let list = movies.filter((m) => (!country || m.country === country)
      && (!type || m.type === type)
      && (!genre || m.genres.includes(genre)));
    if (sort === 'new') list = [...list].sort((a, b) => Number(b.isNew) - Number(a.isNew) || b.year - a.year);
    list = list.slice(0, Number(limit) || 20);
    if (!list.length) {
      slot.remove();
      return;
    }
    const { section, track } = await createRow({ title, seeAllHref: seeAll });
    track.append(...await Promise.all(list.map(createCard)));
    slot.replaceWith(section);
  }));
  refreshArrows();
}

async function init() {
  applyUserOverride();
  await includePartials();
  initHeader();
  markActiveNav();
  initDropdowns();
  initRowScroll();
  document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
  await Promise.all([mountAds(), mountMovieRows()]);
}

// Page scripts can `await ready` before touching shared markup
export const ready = init();
