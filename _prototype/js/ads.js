import { getTemplate } from './include.js';
import { loadJSON } from './data.js';

export const isVip = () => document.body.dataset.user === 'vip';

async function houseAd() {
  const tpl = await getTemplate('ad-slot', 'tpl-ad-house');
  return tpl.content.firstElementChild.cloneNode(true);
}

function paidAd(ad) {
  const link = document.createElement('a');
  link.href = ad.href;
  link.target = '_blank';
  link.rel = 'sponsored noopener';
  link.className = 'block size-full';

  const picture = document.createElement('picture');
  const source = document.createElement('source');
  source.media = '(min-width: 768px)';
  source.srcset = ad.desktop;
  const img = document.createElement('img');
  img.src = ad.mobile;
  img.alt = ad.alt;
  img.loading = 'lazy';
  img.decoding = 'async';
  img.className = 'size-full object-contain';
  picture.append(source, img);
  link.append(picture);
  return { link, img };
}

async function fillSlot(slot, ads) {
  const frag = (await getTemplate('ad-slot', 'tpl-ad')).content.cloneNode(true);
  const creative = frag.querySelector('[data-field="creative"]');
  slot.replaceChildren(frag);
  slot.setAttribute('aria-label', 'Quảng cáo');

  const ad = ads[slot.dataset.slot];
  if (!ad) {
    creative.append(await houseAd());
    return;
  }
  const { link, img } = paidAd(ad);
  img.addEventListener('error', async () => link.replaceWith(await houseAd()), { once: true });
  creative.append(link);
}

// Fills every <aside class="ad-slot" data-slot="..."> on the page. Skipped for VIP.
export async function mountAds(root = document) {
  if (isVip()) return;
  const slots = [...root.querySelectorAll('.ad-slot[data-slot]:not([data-filled])')];
  if (!slots.length) return;

  let ads = {};
  try {
    ads = await loadJSON('ads');
  } catch {
    // No ad server response: every slot falls back to the house ad
  }
  await Promise.all(slots.map((slot) => {
    slot.dataset.filled = '';
    return fillSlot(slot, ads);
  }));
}
