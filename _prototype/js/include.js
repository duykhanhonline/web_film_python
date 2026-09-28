// Loads HTML partials. Needs an HTTP server (fetch does not work on file://).

const cache = new Map();

function fetchPartial(name) {
  if (!cache.has(name)) {
    cache.set(name, fetch(`partials/${name}.html`).then((res) => {
      if (!res.ok) throw new Error(`Không tải được partials/${name}.html`);
      return res.text();
    }));
  }
  return cache.get(name);
}

// Replaces every <div data-include="name"> content with partials/name.html
export async function includePartials(root = document) {
  const slots = [...root.querySelectorAll('[data-include]')];
  await Promise.all(slots.map(async (slot) => {
    slot.innerHTML = await fetchPartial(slot.dataset.include);
  }));
}

const mounted = new Map();

// Mounts partials/<file>.html once, so its <template>s can be found by id
function mountTemplates(file) {
  if (!mounted.has(file)) {
    mounted.set(file, fetchPartial(file).then((html) => {
      const holder = document.createElement('div');
      holder.hidden = true;
      holder.innerHTML = html;
      document.body.append(holder);
    }));
  }
  return mounted.get(file);
}

export async function getTemplate(file, id) {
  await mountTemplates(file);
  return document.getElementById(id);
}

// Clones a template and returns the first element plus a field lookup helper
export function cloneTemplate(tpl) {
  const el = tpl.content.firstElementChild.cloneNode(true);
  const field = (name) => el.querySelector(`[data-field="${name}"]`);
  return { el, field };
}
