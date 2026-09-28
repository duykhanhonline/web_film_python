from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Max, Q
from django.urls import reverse
from django.utils import timezone

from ..images import BACKDROP_WIDTHS, POSTER_WIDTHS, make_renditions
from ..text import normalize_vi, slugify_vi
from ..validators import IMAGE_VALIDATORS, TRAILER_VALIDATORS
from .country import Country
from .genre import Genre

NEW_EPISODE_DAYS = 7


class MovieQuerySet(models.QuerySet):
    def free(self):
        return self.filter(access=Movie.Access.FREE)

    def vip(self):
        return self.filter(access=Movie.Access.VIP)

    def series(self):
        return self.filter(kind=Movie.Kind.SERIES)

    def movies(self):
        return self.filter(kind=Movie.Kind.MOVIE)

    def for_cards(self):
        """Everything a poster card needs, in a fixed number of queries."""
        published = Q(seasons__episodes__published_at__lte=timezone.now())
        return (
            self.select_related("country")
            .prefetch_related("genres")
            .annotate(
                episode_count=Count("seasons__episodes", filter=published),
                latest_episode_at=Max("seasons__episodes__published_at", filter=published),
            )
        )

    def new_episodes(self):
        return self.series().for_cards().order_by("-latest_episode_at", "-year")

    def trending(self):
        return self.order_by("-view_count", "-year")

    def search(self, query: str):
        needle = normalize_vi(query)
        if not needle:
            return self
        return self.filter(search_text__icontains=needle)


class Movie(models.Model):
    class Kind(models.TextChoices):
        SERIES = "bo", "Phim bộ"
        MOVIE = "le", "Phim lẻ"

    class Access(models.TextChoices):
        FREE = "free", "Miễn phí"
        VIP = "vip", "VIP"

    class AgeRating(models.TextChoices):
        P = "P", "P"
        K = "K", "K"
        T13 = "T13", "T13"
        T16 = "T16", "T16"
        T18 = "T18", "T18"

    title = models.CharField("tên phim", max_length=255)
    original_title = models.CharField("tên gốc", max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    kind = models.CharField("loại", max_length=2, choices=Kind.choices)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="movies", verbose_name="quốc gia"
    )
    genres = models.ManyToManyField(Genre, related_name="movies", verbose_name="thể loại")
    year = models.PositiveSmallIntegerField(
        "năm", validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    age_rating = models.CharField(
        "phân loại độ tuổi", max_length=3, choices=AgeRating.choices, default=AgeRating.K
    )
    has_vietsub = models.BooleanField("Vietsub", default=True)
    has_thuyet_minh = models.BooleanField("Thuyết minh", default=False)
    has_long_tieng = models.BooleanField("Lồng tiếng", default=False)
    access = models.CharField(
        "quyền xem", max_length=4, choices=Access.choices, default=Access.FREE
    )
    synopsis = models.TextField("nội dung", blank=True)
    poster = models.ImageField("áp phích (2:3)", upload_to="posters/", validators=IMAGE_VALIDATORS)
    backdrop = models.ImageField(
        "ảnh nền (16:9)", upload_to="backdrops/", validators=IMAGE_VALIDATORS
    )
    trailer = models.FileField(
        "trailer (MP4)",
        upload_to="trailers/",
        blank=True,
        validators=TRAILER_VALIDATORS,
        help_text="MP4 ngắn (30–90 giây, 720p). Tự phát không tiếng trên banner ở máy tính.",
    )
    duration_minutes = models.PositiveSmallIntegerField("thời lượng (phút)", null=True, blank=True)
    total_episodes = models.PositiveSmallIntegerField("tổng số tập", null=True, blank=True)
    schedule_text = models.CharField(
        "lịch chiếu", max_length=255, blank=True, help_text="Ví dụ: Cập nhật thứ 3, 4 hàng tuần"
    )
    view_count = models.PositiveIntegerField("lượt xem", default=0)
    search_text = models.CharField(max_length=520, editable=False, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MovieQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "phim"
        verbose_name_plural = "phim"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        self.search_text = normalize_vi(f"{self.title} {self.original_title}")
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)
        make_renditions(self.poster, POSTER_WIDTHS)
        make_renditions(self.backdrop, BACKDROP_WIDTHS)

    def get_absolute_url(self) -> str:
        return reverse("catalog:detail", kwargs={"slug": self.slug})

    def _unique_slug(self) -> str:
        base = slugify_vi(self.title)[:240] or "phim"
        slug, n = base, 2
        while Movie.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug, n = f"{base}-{n}", n + 1
        return slug

    def clean(self) -> None:
        if not (self.has_vietsub or self.has_thuyet_minh or self.has_long_tieng):
            raise ValidationError("Chọn ít nhất một loại âm thanh.")

    def get_watch_url(self, episode_number: int = 1, season_number: int = 1) -> str:
        if not self.is_series:
            return reverse("player:watch", kwargs={"slug": self.slug})
        url = reverse("player:watch", kwargs={"slug": self.slug, "number": episode_number})
        return f"{url}?phan={season_number}" if season_number > 1 else url

    @property
    def is_series(self) -> bool:
        return self.kind == self.Kind.SERIES

    @property
    def is_vip(self) -> bool:
        return self.access == self.Access.VIP

    @property
    def audio_labels(self) -> list[str]:
        flags = [
            (self.has_vietsub, "Vietsub"),
            (self.has_thuyet_minh, "Thuyết minh"),
            (self.has_long_tieng, "Lồng tiếng"),
        ]
        return [label for on, label in flags if on]

    @property
    def is_new(self) -> bool:
        """True when an episode was published in the last few days."""
        latest = getattr(self, "latest_episode_at", None)
        if latest is None:
            return False
        return latest >= timezone.now() - timedelta(days=NEW_EPISODE_DAYS)
