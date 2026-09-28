from django.db import models


class Genre(models.Model):
    name = models.CharField("tên", max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "thể loại"
        verbose_name_plural = "thể loại"

    def __str__(self) -> str:
        return self.name
