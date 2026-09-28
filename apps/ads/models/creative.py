from django.db import models

from apps.catalog.validators import IMAGE_VALIDATORS

from .ad_slot import AdSlot
from .base import Scheduled


class Creative(Scheduled):
    slot = models.ForeignKey(AdSlot, on_delete=models.CASCADE, related_name="creatives")
    name = models.CharField("tên", max_length=255)
    image_desktop = models.ImageField("ảnh desktop", upload_to="ads/", validators=IMAGE_VALIDATORS)
    image_mobile = models.ImageField("ảnh mobile", upload_to="ads/", validators=IMAGE_VALIDATORS)
    link = models.URLField("liên kết")
    alt_text = models.CharField("mô tả ảnh", max_length=255)

    class Meta:
        ordering = ["-starts_at", "-pk"]
        verbose_name = "mẫu quảng cáo"
        verbose_name_plural = "mẫu quảng cáo"

    def __str__(self) -> str:
        return self.name
