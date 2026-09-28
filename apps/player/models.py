from django.conf import settings
from django.db import models

from apps.catalog.models import Episode


class WatchProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watch_progress"
    )
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="+")
    position_seconds = models.PositiveIntegerField("vị trí (giây)", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "episode"], name="unique_watch_progress")
        ]
        verbose_name = "tiến độ xem"
        verbose_name_plural = "tiến độ xem"

    def __str__(self) -> str:
        return f"{self.user} - {self.episode}"

    @property
    def movie(self):
        return self.episode.season.movie

    @property
    def watch_url(self) -> str:
        return self.movie.get_watch_url(self.episode.number, self.episode.season.number)

    @property
    def percent(self) -> int:
        duration = self.episode.duration
        if not duration:
            return 0
        return min(100, round(self.position_seconds * 100 / duration))

    @property
    def remaining_seconds(self) -> int:
        return max(0, self.episode.duration - self.position_seconds)
