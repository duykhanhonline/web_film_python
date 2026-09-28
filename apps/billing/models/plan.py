from django.db import models


class Plan(models.Model):
    name = models.CharField("tên gói", max_length=100)
    months = models.PositiveSmallIntegerField("số tháng")
    price_vnd = models.PositiveIntegerField("giá (VND)")
    is_best_value = models.BooleanField("tiết kiệm nhất", default=False)
    is_active = models.BooleanField("đang bán", default=True)

    class Meta:
        ordering = ["months"]
        verbose_name = "gói VIP"
        verbose_name_plural = "gói VIP"

    def __str__(self) -> str:
        return self.name

    @property
    def price_per_month(self) -> int:
        return self.price_vnd // self.months
