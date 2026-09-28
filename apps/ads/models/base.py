from django.db import models
from django.db.models import Q
from django.utils import timezone


class ScheduledQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            Q(is_active=True),
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gt=now),
        )


class Scheduled(models.Model):
    is_active = models.BooleanField("đang chạy", default=True)
    starts_at = models.DateTimeField("bắt đầu", null=True, blank=True)
    ends_at = models.DateTimeField("kết thúc", null=True, blank=True)

    objects = ScheduledQuerySet.as_manager()

    class Meta:
        abstract = True
