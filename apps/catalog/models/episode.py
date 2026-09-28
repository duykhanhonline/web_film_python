from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from .season import Season


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="episodes")
    number = models.PositiveSmallIntegerField("tập")
    title = models.CharField("tên tập", max_length=255, blank=True)
    video = models.FileField(
        "video (MP4)",
        upload_to="videos/",
        blank=True,
        validators=[FileExtensionValidator(["mp4"])],
    )
    duration = models.PositiveIntegerField("thời lượng (giây)", default=0)
    intro_end = models.PositiveIntegerField(
        "hết giới thiệu (giây)", default=0, help_text="Dùng cho nút “Bỏ qua giới thiệu”."
    )
    published_at = models.DateTimeField("ngày phát hành", default=timezone.now)

    class Meta:
        ordering = ["season", "number"]
        constraints = [
            models.UniqueConstraint(fields=["season", "number"], name="unique_episode_number")
        ]
        verbose_name = "tập"
        verbose_name_plural = "tập"

    def __str__(self) -> str:
        return f"{self.season.movie} - Tập {self.number}"
