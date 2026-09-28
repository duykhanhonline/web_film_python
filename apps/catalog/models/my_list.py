from django.conf import settings
from django.db import models

from .movie import Movie


class MyListItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="my_list"
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "movie"], name="unique_my_list_item")
        ]
        verbose_name = "danh sách của tôi"
        verbose_name_plural = "danh sách của tôi"

    def __str__(self) -> str:
        return f"{self.user} - {self.movie}"
