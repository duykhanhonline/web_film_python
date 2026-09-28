from django.db import models


class Country(models.Model):
    name = models.CharField("tên", max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveSmallIntegerField("thứ tự", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "quốc gia"
        verbose_name_plural = "quốc gia"

    def __str__(self) -> str:
        return self.name
