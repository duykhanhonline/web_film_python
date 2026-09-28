from django.db import models


class AdSlot(models.Model):
    class Code(models.TextChoices):
        BILLBOARD = "ad-billboard", "Billboard dưới banner"
        INFEED = "ad-infeed", "Giữa các hàng phim"
        SIDEBAR = "ad-sidebar", "Cột phải trang chi tiết"

    code = models.CharField("mã vị trí", max_length=40, choices=Code.choices, unique=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "vị trí quảng cáo"
        verbose_name_plural = "vị trí quảng cáo"

    def __str__(self) -> str:
        return self.get_code_display()
