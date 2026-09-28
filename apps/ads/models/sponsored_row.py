from django.db import models

from apps.catalog.models import Movie

from .base import Scheduled


class SponsoredRow(Scheduled):
    title = models.CharField("tiêu đề hàng", max_length=255)
    sponsor_name = models.CharField("nhà tài trợ", max_length=255)
    movies = models.ManyToManyField(Movie, related_name="+", verbose_name="phim")

    class Meta:
        ordering = ["-starts_at", "-pk"]
        verbose_name = "hàng phim tài trợ"
        verbose_name_plural = "hàng phim tài trợ"

    def __str__(self) -> str:
        return f"{self.title} · {self.sponsor_name}"
