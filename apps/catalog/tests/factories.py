import io
import itertools
import shutil
import tempfile
from datetime import timedelta

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from apps.catalog.models import Country, Episode, Genre, Movie, Season

_counter = itertools.count()
_TEMP_MEDIA = tempfile.mkdtemp(prefix="phimhay-test-media-")


def image_file(size: tuple[int, int] = (40, 60)) -> ContentFile:
    buf = io.BytesIO()
    Image.new("RGB", size, (30, 40, 70)).save(buf, "WEBP")
    return ContentFile(buf.getvalue())


def make_country(name: str = "Hàn Quốc", slug: str = "han-quoc") -> Country:
    return Country.objects.get_or_create(slug=slug, defaults={"name": name})[0]


def make_genre(name: str = "Tình cảm", slug: str = "tinh-cam") -> Genre:
    return Genre.objects.get_or_create(slug=slug, defaults={"name": name})[0]


def make_movie(
    title: str | None = None,
    *,
    kind: str = Movie.Kind.SERIES,
    access: str = Movie.Access.FREE,
    episodes: int = 3,
    latest_days_ago: int = 30,
    country: Country | None = None,
    genres: list[Genre] | None = None,
    **fields,
) -> Movie:
    n = next(_counter)
    movie = Movie(
        title=title or f"Phim {n}",
        kind=kind,
        access=access,
        country=country or make_country(),
        year=2024,
        **fields,
    )
    movie.poster.save(f"p{n}.webp", image_file(), save=False)
    movie.backdrop.save(f"b{n}.webp", image_file((64, 36)), save=False)
    movie.save()
    movie.genres.set(genres or [make_genre()])
    season = Season.objects.create(movie=movie, number=1)
    count = episodes if kind == Movie.Kind.SERIES else 1
    latest = timezone.now() - timedelta(days=latest_days_ago)
    for number in range(1, count + 1):
        Episode.objects.create(
            season=season,
            number=number,
            duration=2700,
            published_at=latest - timedelta(days=7 * (count - number)),
        )
    return movie


@override_settings(MEDIA_ROOT=_TEMP_MEDIA)
class MediaTestCase(TestCase):
    """TestCase that writes uploads to a temp folder, not media/."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_TEMP_MEDIA, ignore_errors=True)
