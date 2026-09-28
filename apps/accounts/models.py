from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(r"^0\d{9}$", "Số điện thoại gồm 10 chữ số và bắt đầu bằng 0.")


class User(AbstractUser):
    phone = models.CharField(
        "số điện thoại",
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[phone_validator],
    )

    class Meta:
        verbose_name = "người dùng"
        verbose_name_plural = "người dùng"

    def __str__(self) -> str:
        return self.phone or self.username
