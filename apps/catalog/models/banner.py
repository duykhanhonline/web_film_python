from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from ..images import BACKDROP_WIDTHS, make_renditions
from ..validators import IMAGE_VALIDATORS
from .movie import Movie


class BannerQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            Q(is_active=True),
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gt=now),
        )


class Banner(models.Model):
    """A hero carousel slide: a movie, or sponsored content (ad-hero-slide)."""

    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, blank=True, related_name="banners"
    )
    title = models.CharField("tiêu đề (quảng cáo)", max_length=255, blank=True)
    synopsis = models.CharField("mô tả ngắn (quảng cáo)", max_length=300, blank=True)
    sponsor_name = models.CharField("nhà tài trợ", max_length=255, blank=True)
    image = models.ImageField(
        "ảnh (quảng cáo)", upload_to="banners/", blank=True, validators=IMAGE_VALIDATORS
    )
    link = models.URLField("liên kết (quảng cáo)", blank=True)
    order = models.PositiveSmallIntegerField("thứ tự", default=0)
    is_active = models.BooleanField("đang hiển thị", default=True)
    starts_at = models.DateTimeField("bắt đầu", null=True, blank=True)
    ends_at = models.DateTimeField("kết thúc", null=True, blank=True)

    objects = BannerQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = "banner"
        verbose_name_plural = "banner"

    def __str__(self) -> str:
        return str(self.movie) if self.movie_id else f"Quảng cáo: {self.title}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        make_renditions(self.image, BACKDROP_WIDTHS)

    @property
    def is_sponsored(self) -> bool:
        return self.movie_id is None

    def clean(self) -> None:
        if self.movie_id:
            return
        missing = [
            label
            for value, label in [
                (self.title, "tiêu đề"),
                (self.sponsor_name, "nhà tài trợ"),
                (self.image, "ảnh"),
                (self.link, "liên kết"),
            ]
            if not value
        ]
        if missing:
            raise ValidationError(
                "Chọn một phim, hoặc nhập đủ nội dung quảng cáo: " + ", ".join(missing) + "."
            )
