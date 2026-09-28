// "Danh sách của tôi" toggle. Button: <button data-mylist="{toggle url}" data-movie="{slug}">
const csrfToken = () => document.querySelector('meta[name="csrf-token"]')?.content ?? '';

function setState(slug, inList) {
  document.querySelectorAll(`[data-mylist][data-movie="${CSS.escape(slug)}"]`).forEach((btn) => {
    btn.setAttribute('aria-pressed', String(inList));
    const label = btn.querySelector('[data-mylist-label]');
    if (label) label.textContent = inList ? 'Đã thêm' : 'Danh sách';
  });
}

export function initMyList(root = document) {
  root.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-mylist]');
    if (!btn || btn.dataset.busy) return;
    btn.dataset.busy = '';
    try {
      const res = await fetch(btn.dataset.mylist, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken(), Accept: 'application/json' },
        credentials: 'same-origin',
      });
      const data = await res.json();
      if (res.status === 401) {
        location.href = `${data.login_url}?next=${encodeURIComponent(location.pathname)}`;
        return;
      }
      if (res.ok) setState(btn.dataset.movie, data.in_list);
    } catch {
      // Network error: leave the button as it was
    } finally {
      delete btn.dataset.busy;
    }
  });
}
