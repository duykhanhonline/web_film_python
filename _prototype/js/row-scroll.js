import { getTemplate, cloneTemplate } from './include.js';

// Builds an empty row section. Append cards to the returned `track`.
export async function createRow({ title, seeAllHref, sponsor }) {
  const { el, field } = cloneTemplate(await getTemplate('row', 'tpl-row'));
  const id = `row-${Math.random().toString(36).slice(2, 8)}`;
  const heading = field('title');
  heading.id = id;
  heading.textContent = title;
  el.setAttribute('aria-labelledby', id);

  if (sponsor) {
    const label = field('sponsor');
    label.textContent = `Được tài trợ bởi ${sponsor}`;
    label.hidden = false;
  }

  const seeAll = field('see-all');
  if (seeAllHref) {
    seeAll.href = seeAllHref;
    seeAll.setAttribute('aria-label', `Xem tất cả ${title}`);
  } else {
    seeAll.remove();
  }
  return { section: el, track: el.querySelector('[data-row-track]') };
}

function updateArrows(track) {
  const section = track.closest('section');
  const prev = section?.querySelector('[data-row-prev]');
  const next = section?.querySelector('[data-row-next]');
  if (!prev || !next) return;
  prev.disabled = track.scrollLeft <= 4;
  next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
}

// One delegated listener handles every row on the page
export function initRowScroll(root = document) {
  root.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-row-prev], [data-row-next]');
    if (!btn) return;
    const track = btn.closest('section').querySelector('[data-row-track]');
    const dir = btn.hasAttribute('data-row-next') ? 1 : -1;
    track.scrollBy({ left: dir * track.clientWidth * 0.9 });
  });

  root.addEventListener('scroll', (e) => {
    if (e.target.matches?.('[data-row-track]')) updateArrows(e.target);
  }, { capture: true, passive: true });
}

export function refreshArrows(root = document) {
  root.querySelectorAll('[data-row-track]').forEach(updateArrows);
}
