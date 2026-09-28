// Strips Vietnamese diacritics so "hau due" matches "Hậu Duệ"
export function normalizeVi(str) {
  return String(str)
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase()
    .trim();
}

const vnd = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' });
const num = new Intl.NumberFormat('vi-VN');

export const formatVND = (amount) => vnd.format(amount);
export const formatNumber = (n) => num.format(n);

// dd/mm/yyyy
export function formatDate(input) {
  const d = new Date(input);
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

// "1:05:30" or "12:04"
export function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const pad = (n) => String(n).padStart(2, '0');
  return h ? `${h}:${pad(m)}:${pad(s % 60)}` : `${m}:${pad(s % 60)}`;
}

// Placeholder image URLs in data use {w} and {h} tokens
export function imageUrl(pattern, w, h) {
  return pattern.replace('{w}', w).replace('{h}', h);
}
