import './main.js';
import { cloneTemplate } from './include.js';
import { getMovies, loadJSON } from './data.js';
import { createCard, createRankCard, createContinueCard } from './card.js';
import { createRow, refreshArrows } from './row-scroll.js';
import { initCarousel } from './carousel.js';
import { initMyList } from './my-list.js';
import { isVip } from './ads.js';
import { imageUrl } from './utils.js';

const byId = (movies) => new Map(movies.map((m) => [m.id, m]));

function badge(text, className) {
  const el = document.createElement('span');
  el.className = className;
  el.textContent = text;
  return el;
}

function heroBadges(movie) {
  const meta = 'text-text/90';
  const parts = [
    badge(movie.access === 'vip' ? 'VIP' : 'Miễn phí', `badge ${movie.access === 'vip' ? 'badge-vip' : 'badge-free'}`),
    movie.isNew && badge('Mới', 'badge badge-new'),
    badge(movie.ageRating, 'badge border border-text/40 text-text'),
    badge(String(movie.year), meta),
    badge(movie.country, meta),
    badge(movie.type === 'bo' ? `Tập ${movie.episodes.current}/${movie.episodes.total}` : `${movie.duration} phút`, meta),
    badge(movie.audio.join(' · '), meta),
  ];
  return parts.filter(Boolean);
}

function setImages(field, pattern, alt, eager) {
  const attr = eager ? 'srcset' : 'data-srcset';
  field('source-lg').setAttribute(attr, imageUrl(pattern, 1920, 823));
  field('source-md').setAttribute(attr, imageUrl(pattern, 1280, 720));
  const img = field('backdrop');
  img.setAttribute(eager ? 'src' : 'data-src', imageUrl(pattern, 720, 960));
  img.alt = alt;
  if (eager) {
    img.loading = 'eager';
    img.fetchPriority = 'high';
  }
}

function heroSlide(tpl, banner, movie, i, total) {
  const { el, field } = cloneTemplate(tpl);
  el.setAttribute('aria-label', `${i + 1} / ${total}`);

  if (banner.sponsored) {
    setImages(field, banner.backdrop, `Quảng cáo: ${banner.title}`, i === 0);
    const sponsor = field('sponsor');
    sponsor.textContent = `Quảng cáo · Được tài trợ bởi ${banner.sponsor}`;
    sponsor.hidden = false;
    field('title').textContent = banner.title;
    field('original').remove();
    field('badges').remove();
    field('synopsis').textContent = banner.synopsis;
    const cta = field('cta');
    cta.href = banner.href;
    cta.target = '_blank';
    cta.rel = 'sponsored noopener';
    field('cta-label').textContent = 'Tìm hiểu thêm';
    field('mylist').remove();
    return el;
  }

  setImages(field, movie.backdrop, `Ảnh nền phim ${movie.title}`, i === 0);
  field('title').textContent = movie.title;
  field('original').textContent = movie.originalTitle;
  field('badges').append(...heroBadges(movie));
  field('synopsis').textContent = movie.synopsis;
  field('cta').href = `xem-phim.html?id=${encodeURIComponent(movie.id)}`;
  field('cta').setAttribute('aria-label', `Xem ngay ${movie.title}`);
  field('mylist').dataset.mylist = movie.id;
  field('mylist').setAttribute('aria-label', `Thêm ${movie.title} vào danh sách`);
  return el;
}

async function renderHero(movies) {
  const root = document.querySelector('[data-carousel]');
  if (!root) return;
  const banners = (await loadJSON('banners')).filter((b) => !(b.sponsored && isVip()));
  const tpl = document.getElementById('tpl-hero-slide');
  const slides = banners
    .map((b) => ({ banner: b, movie: movies.get(b.movieId) }))
    .filter(({ banner, movie }) => banner.sponsored || movie)
    .map(({ banner, movie }, i, all) => heroSlide(tpl, banner, movie, i, all.length));

  const track = root.querySelector('[data-carousel-track]');
  track.append(...slides);
  track.classList.remove('skeleton');
  initCarousel(root);
}

async function replaceWithRow(slot, options, cards) {
  if (!slot) return;
  if (!cards.length) {
    slot.remove();
    return;
  }
  const { section, track } = await createRow(options);
  track.append(...cards);
  if (slot.hasAttribute('data-ad')) section.dataset.ad = '';
  slot.replaceWith(section);
}

async function renderContinue(movies, home) {
  const items = home.continueWatching.filter((p) => movies.has(p.movieId));
  const cards = await Promise.all(items.map((p) => createContinueCard(movies.get(p.movieId), p)));
  await replaceWithRow(document.querySelector('[data-home="continue"]'), { title: 'Xem tiếp' }, cards);
}

async function renderTop10(movies, home) {
  const list = home.top10.map((id) => movies.get(id)).filter(Boolean).slice(0, 10);
  const cards = await Promise.all(list.map((m, i) => createRankCard(m, i + 1)));
  await replaceWithRow(document.querySelector('[data-home="top10"]'), { title: 'Top 10 hôm nay' }, cards);
}

async function renderSponsoredRow(movies) {
  const slot = document.querySelector('[data-home="sponsored"]');
  if (!slot) return;
  const row = !isVip() && (await loadJSON('ads').catch(() => ({})))['ad-sponsored-row'];
  if (!row) {
    slot.remove();
    return;
  }
  const list = row.movieIds.map((id) => movies.get(id)).filter(Boolean);
  const cards = await Promise.all(list.map(createCard));
  await replaceWithRow(slot, { title: row.title, sponsor: row.sponsor }, cards);
}

async function init() {
  const [movieList, home] = await Promise.all([getMovies(), loadJSON('home')]);
  const movies = byId(movieList);
  await Promise.all([
    renderHero(movies),
    renderContinue(movies, home),
    renderTop10(movies, home),
    renderSponsoredRow(movies),
  ]);
  initMyList();
  refreshArrows();
}

init();
