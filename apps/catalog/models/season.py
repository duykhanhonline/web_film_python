from django.db import models

from .movie import Movie


class Season(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="seasons")
    number = models.PositiveSmallIntegerField("phần", default=1)
    title = models.CharField("tên phần", max_length=255, blank=True)

    class Meta:
        ordering = ["movie", "number"]
        constraints = [
            models.UniqueConstraint(fields=["movie", "number"], name="unique_season_number")
        ]
        verbose_name = "phần"
        verbose_name_plural = "phần"

    def __str__(self) -> str:
        return f"{self.movie} - Phần {self.number}"
