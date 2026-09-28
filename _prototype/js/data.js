const cache = new Map();

export function loadJSON(name) {
  if (!cache.has(name)) {
    cache.set(name, fetch(`data/${name}.json`).then((res) => {
      if (!res.ok) throw new Error(`Không tải được data/${name}.json`);
      return res.json();
    }));
  }
  return cache.get(name);
}

export const getMovies = () => loadJSON('movies');

export async function getMovie(id) {
  const movies = await getMovies();
  return movies.find((m) => m.id === id);
}
