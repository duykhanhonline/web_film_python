// Swaps a paid creative for the house ad (VIP promo) when its image fails to load.
function fallBack(img) {
  const slot = img.closest('.ad-slot');
  const tpl = slot?.querySelector('template[data-house-ad]');
  if (!tpl) return;
  slot.querySelector('[data-ad-creative]')?.replaceWith(tpl.content.cloneNode(true));
  tpl.remove();
}

export function initAds(root = document) {
  const images = root.querySelectorAll('[data-ad-creative] img');
  images.forEach((img) => {
    // The image may have failed before this module ran
    if (img.complete && img.naturalWidth === 0 && img.currentSrc) fallBack(img);
    else img.addEventListener('error', () => fallBack(img), { once: true });
  });
}
