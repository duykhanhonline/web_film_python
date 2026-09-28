from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.billing.models import Plan, Subscription
from apps.billing.templatetags.billing_tags import vnd
from apps.billing.tier import FREE, VIP, get_user_tier


class VndFilterTests(TestCase):
    def test_formats_vietnamese_dong(self):
        self.assertEqual(vnd(99000), "99.000 ₫")
        self.assertEqual(vnd(1234567), "1.234.567 ₫")
        self.assertEqual(vnd(0), "0 ₫")


class TierTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("chi", password="x")
        cls.plan = Plan.objects.create(name="Gói 1 tháng", months=1, price_vnd=99_000)

    def tier_for(self, user) -> str:
        request = RequestFactory().get("/")
        request.user = user
        return get_user_tier(request)

    def test_free_without_subscription(self):
        self.assertEqual(self.tier_for(self.user), FREE)

    def test_vip_with_active_subscription(self):
        now = timezone.now()
        Subscription.objects.create(
            user=self.user, plan=self.plan, starts_at=now, ends_at=now + timedelta(days=30)
        )
        self.assertEqual(self.tier_for(self.user), VIP)

    def test_expired_subscription_is_free(self):
        now = timezone.now()
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            starts_at=now - timedelta(days=40),
            ends_at=now - timedelta(days=10),
        )
        self.assertEqual(self.tier_for(self.user), FREE)

    def test_plans_page_shows_vnd_prices(self):
        Plan.objects.create(name="Gói 12 tháng", months=12, price_vnd=899_000, is_best_value=True)
        response = self.client.get(reverse("billing:plans"))
        self.assertContains(response, "99.000 ₫")
        self.assertContains(response, "Tiết kiệm nhất")
