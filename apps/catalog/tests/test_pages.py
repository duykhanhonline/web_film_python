from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.ads.models import AdSlot
from apps.billing.models import Plan, Subscription
from apps.catalog.models import Banner, Movie, MyListItem
from apps.player.models import WatchProgress

from .factories import MediaTestCase, make_country, make_movie


def make_vip(user) -> None:
    plan = Plan.objects.create(name="Gói 1 tháng", months=1, price_vnd=99_000)
    now = timezone.now()
    Subscription.objects.create(
        user=user, plan=plan, starts_at=now - timedelta(days=1), ends_at=now + timedelta(days=5)
    )


class HomePageTests(MediaTestCase):
    @classmethod
    def setUpTestData(cls):
        korea = make_country()
        cls.movies = [make_movie(country=korea) for _ in range(6)]
        cls.new_movie = make_movie("Phim Mới Ra", latest_days_ago=1, country=korea)
        Banner.objects.create(movie=cls.new_movie)
        for code in AdSlot.Code.values:
            AdSlot.objects.create(code=code)
        cls.user = get_user_model().objects.create_user("an", password="x")

    def setUp(self):
        cache.clear()

    def test_home_renders_rows_and_hero(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top 10 hôm nay")
        self.assertContains(response, "Phim bộ mới cập nhật")
        self.assertContains(response, "Phim Mới Ra")
        self.assertContains(response, 'fetchpriority="high"')
        self.assertContains(response, "<h1", count=1)

    def test_hero_trailer_is_deferred_until_js_plays_it(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertNotContains(response, "data-trailer")
        self.assertNotContains(response, "Xem trailer")

        self.new_movie.trailer.save("t.mp4", ContentFile(b"\x00" * 16))
        cache.clear()
        response = self.client.get(reverse("catalog:home"))
        self.assertContains(response, f'data-src="{self.new_movie.trailer.url}"')
        self.assertContains(response, 'preload="none"')
        self.assertContains(response, "data-trailer-play")
        self.assertContains(response, "Xem trailer")
        self.assertNotContains(response, f' src="{self.new_movie.trailer.url}"')

    def test_new_badge_is_computed_from_latest_episode(self):
        movie = Movie.objects.for_cards().get(pk=self.new_movie.pk)
        self.assertTrue(movie.is_new)
        old = Movie.objects.for_cards().get(pk=self.movies[0].pk)
        self.assertFalse(old.is_new)
        self.assertEqual(old.episode_count, 3)

    def test_free_user_sees_ads(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertContains(response, 'data-slot="ad-billboard"')
        self.assertContains(response, "Quảng cáo")
        self.assertContains(response, 'data-user="free"')

    def test_vip_user_gets_no_ad_markup(self):
        make_vip(self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse("catalog:home"))
        self.assertContains(response, 'data-user="vip"')
        self.assertNotContains(response, "ad-slot")
        self.assertNotContains(response, "Nâng cấp VIP")

    def test_continue_row_only_for_logged_in_users(self):
        episode = self.movies[0].seasons.get().episodes.get(number=2)
        WatchProgress.objects.create(user=self.user, episode=episode, position_seconds=600)
        self.assertNotContains(self.client.get(reverse("catalog:home")), "Xem tiếp")

        self.client.force_login(self.user)
        response = self.client.get(reverse("catalog:home"))
        self.assertContains(response, "Xem tiếp")
        self.assertContains(response, reverse("player:watch", args=[self.movies[0].slug, 2]))

    def test_home_query_count_does_not_grow_with_movies(self):
        with CaptureQueriesContext(connection) as before:
            self.client.get(reverse("catalog:home"))
        make_movie(country=make_country())
        make_movie(country=make_country())
        cache.clear()
        with CaptureQueriesContext(connection) as after:
            self.client.get(reverse("catalog:home"))
        self.assertEqual(len(before), len(after))

    def test_home_rows_are_cached(self):
        self.client.get(reverse("catalog:home"))
        with CaptureQueriesContext(connection) as cached:
            self.client.get(reverse("catalog:home"))
        # Only per-request work left: session, user tier, ad creatives
        self.assertLess(len(cached), 6)


class ListingPageTests(MediaTestCase):
    @classmethod
    def setUpTestData(cls):
        make_movie("Phim Bộ Một")
        make_movie("Phim Lẻ Một", kind=Movie.Kind.MOVIE, duration_minutes=95)

    def test_series_and_movies_pages(self):
        response = self.client.get(reverse("catalog:series"))
        self.assertContains(response, "Phim Bộ Một")
        self.assertNotContains(response, "Phim Lẻ Một")
        self.assertContains(response, 'aria-current="page"')

        response = self.client.get(reverse("catalog:movies"))
        self.assertContains(response, "Phim Lẻ Một")
        self.assertNotContains(response, "Phim Bộ Một")

    def test_listing_query_count_does_not_grow_with_movies(self):
        cache.clear()
        with CaptureQueriesContext(connection) as before:
            self.client.get(reverse("catalog:series"))
        make_movie()
        make_movie()
        cache.clear()
        with CaptureQueriesContext(connection) as after:
            self.client.get(reverse("catalog:series"))
        self.assertEqual(len(before), len(after))

    def test_detail_page(self):
        movie = Movie.objects.get(title="Phim Bộ Một")
        response = self.client.get(movie.get_absolute_url())
        self.assertContains(response, "Phim Bộ Một")
        self.assertContains(response, 'property="og:title"')


class MyListTests(MediaTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie = make_movie()
        cls.user = get_user_model().objects.create_user("binh", password="x")

    def test_anonymous_gets_login_url(self):
        response = self.client.post(reverse("catalog:my_list_toggle", args=[self.movie.slug]))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["login_url"], reverse("accounts:login"))

    def test_toggle_adds_then_removes(self):
        self.client.force_login(self.user)
        url = reverse("catalog:my_list_toggle", args=[self.movie.slug])
        self.assertEqual(self.client.post(url).json(), {"in_list": True})
        self.assertTrue(MyListItem.objects.filter(user=self.user, movie=self.movie).exists())
        self.assertEqual(self.client.post(url).json(), {"in_list": False})
        self.assertFalse(MyListItem.objects.exists())

    def test_get_is_not_allowed(self):
        url = reverse("catalog:my_list_toggle", args=[self.movie.slug])
        self.assertEqual(self.client.get(url).status_code, 405)
