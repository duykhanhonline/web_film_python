"""Builds the home page rows. Shared rows are cached; per-user rows are not."""

from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch
from django.urls import reverse

from apps.ads.models import SponsoredRow

from .models import Banner, Movie

ROW_LIMIT = 20
HERO_LIMIT = 5


def _search_url(**params: str) -> str:
    query = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{reverse('catalog:search')}?{query}"


def _row(title: str, movies, see_all_url: str = "", variant: str = "poster") -> dict:
    return {"title": title, "see_all_url": see_all_url, "movies": list(movies), "variant": variant}


def build_rows() -> list[dict]:
    cards = Movie.objects.for_cards()
    rows = [
        _row("Top 10 hôm nay", cards.trending()[:10], variant="rank"),
        _row(
            "Phim bộ mới cập nhật",
            Movie.objects.new_episodes()[:ROW_LIMIT],
            reverse("catalog:series"),
        ),
        _row(
            "Phim Hàn Quốc",
            cards.filter(country__slug="han-quoc").trending()[:ROW_LIMIT],
            _search_url(**{"quoc-gia": "han-quoc"}),
        ),
        _row(
            "Phim Trung Quốc",
            cards.filter(country__slug="trung-quoc").trending()[:ROW_LIMIT],
            _search_url(**{"quoc-gia": "trung-quoc"}),
        ),
        _row(
            "Phim Việt chiếu rạp",
            cards.movies().filter(country__slug="viet-nam").trending()[:ROW_LIMIT],
            _search_url(**{"quoc-gia": "viet-nam", "loai": "phim-le"}),
        ),
        _row(
            "Anime",
            cards.filter(genres__slug="hoat-hinh").distinct().trending()[:ROW_LIMIT],
            _search_url(**{"the-loai": "hoat-hinh"}),
        ),
    ]
    return [row for row in rows if row["movies"]]


def build_banners() -> list[Banner]:
    banners = list(Banner.objects.active().select_related("movie")[:HERO_LIMIT])
    movie_ids = [b.movie_id for b in banners if b.movie_id]
    movies = Movie.objects.for_cards().in_bulk(movie_ids)
    for banner in banners:
        if banner.movie_id:
            banner.movie = movies[banner.movie_id]
    return banners


def build_sponsored_row() -> dict | None:
    sponsored = (
        SponsoredRow.objects.active()
        .prefetch_related(Prefetch("movies", queryset=Movie.objects.for_cards().trending()))
        .first()
    )
    if sponsored is None or not sponsored.movies.all():
        return None
    row = _row(sponsored.title, sponsored.movies.all())
    row["sponsor"] = sponsored.sponsor_name
    return row


def cached_home() -> dict:
    """Shared, non-personal home data. Never put per-user data in here."""
    return cache.get_or_set(
        "home:v1",
        lambda: {
            "banners": build_banners(),
            "rows": build_rows(),
            "sponsored_row": build_sponsored_row(),
        },
        settings.HOME_CACHE_SECONDS,
    )
