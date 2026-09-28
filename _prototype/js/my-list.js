// "Danh sách của tôi": kept in this browser only until there is a backend
const KEY = 'phimhay:my-list';

function read() {
  try {
    return new Set(JSON.parse(localStorage.getItem(KEY)) || []);
  } catch {
    return new Set();
  }
}

function write(ids) {
  try {
    localStorage.setItem(KEY, JSON.stringify([...ids]));
  } catch {
    // Storage blocked: the toggle still works for this page view
  }
}

let saved = read();

export function syncButton(btn) {
  const on = saved.has(btn.dataset.mylist);
  btn.setAttribute('aria-pressed', String(on));
  const label = btn.querySelector('[data-mylist-label]');
  if (label) label.textContent = on ? 'Đã thêm' : 'Danh sách';
}

// Buttons: <button data-mylist="movie-id" aria-pressed="false">…<span data-mylist-label>
export function initMyList(root = document) {
  root.querySelectorAll('[data-mylist]').forEach(syncButton);
  root.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-mylist]');
    if (!btn) return;
    const id = btn.dataset.mylist;
    if (saved.has(id)) saved.delete(id);
    else saved.add(id);
    write(saved);
    document.querySelectorAll(`[data-mylist="${CSS.escape(id)}"]`).forEach(syncButton);
  });
}
