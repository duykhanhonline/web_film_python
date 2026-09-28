import { getTemplate, cloneTemplate } from './include.js';
import { imageUrl, formatTime } from './utils.js';

function fillAccess(badge, movie) {
  const vip = movie.access === 'vip';
  badge.textContent = vip ? 'VIP' : 'Miễn phí';
  badge.classList.add(vip ? 'badge-vip' : 'badge-free');
}

function fillPoster(field, movie) {
  field('link').href = `chi-tiet.html?id=${encodeURIComponent(movie.id)}`;

  const img = field('poster');
  img.src = imageUrl(movie.poster, 400, 600);
  img.srcset = `${imageUrl(movie.poster, 200, 300)} 200w, ${imageUrl(movie.poster, 400, 600)} 400w`;
  img.alt = `Áp phích phim ${movie.title}`;

  fillAccess(field('access'), movie);
  field('new').hidden = !movie.isNew;
  field('audio').textContent = movie.audio[0];

  if (movie.type === 'bo' && movie.episodes) {
    const ep = field('episodes');
    ep.textContent = `Tập ${movie.episodes.current}/${movie.episodes.total}`;
    ep.hidden = false;
  }
  field('title').textContent = movie.title;
}

// Portrait 2:3 poster card
export async function createCard(movie) {
  const { el, field } = cloneTemplate(await getTemplate('card', 'tpl-card'));
  fillPoster(field, movie);
  field('meta').textContent = [movie.year, movie.country, movie.genres.join(', ')].join(' · ');
  field('synopsis').textContent = movie.synopsis;
  return el;
}

// Top 10 card: large outlined rank number beside the poster
export async function createRankCard(movie, rank) {
  const { el, field } = cloneTemplate(await getTemplate('card', 'tpl-card-rank'));
  fillPoster(field, movie);
  field('rank').textContent = rank;
  field('link').setAttribute('aria-label', `Hạng ${rank}: ${movie.title}`);
  return el;
}

// Landscape 16:9 card for "Xem tiếp", with a progress bar
export async function createContinueCard(movie, progress) {
  const { el, field } = cloneTemplate(await getTemplate('card', 'tpl-card-landscape'));

  field('link').href = `xem-phim.html?id=${encodeURIComponent(movie.id)}&tap=${progress.episode ?? 1}`;

  const img = field('backdrop');
  img.src = imageUrl(movie.backdrop, 640, 360);
  img.srcset = `${imageUrl(movie.backdrop, 320, 180)} 320w, ${imageUrl(movie.backdrop, 640, 360)} 640w`;
  img.alt = `Ảnh nền phim ${movie.title}`;

  fillAccess(field('access'), movie);
  const pct = Math.min(100, Math.round((progress.watched / progress.duration) * 100));
  field('progress').style.width = `${pct}%`;
  field('title').textContent = movie.title;
  field('resume').textContent = [
    progress.episode ? `Tập ${progress.episode}` : null,
    `Còn ${formatTime(progress.duration - progress.watched)}`,
  ].filter(Boolean).join(' · ');
  return el;
}
