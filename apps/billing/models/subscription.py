from django.conf import settings
from django.db import models
from django.utils import timezone

from .plan import Plan


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(starts_at__lte=now, ends_at__gt=now)


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    starts_at = models.DateTimeField("bắt đầu", default=timezone.now)
    ends_at = models.DateTimeField("kết thúc")

    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        ordering = ["-starts_at"]
        verbose_name = "thuê bao VIP"
        verbose_name_plural = "thuê bao VIP"

    def __str__(self) -> str:
        return f"{self.user} - {self.plan}"

    @property
    def is_active(self) -> bool:
        return self.starts_at <= timezone.now() < self.ends_at
