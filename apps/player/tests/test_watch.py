from django.urls import reverse

from apps.catalog.models import Movie
from apps.catalog.tests.factories import MediaTestCase, make_movie


class WatchViewTests(MediaTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.free = make_movie("Phim Miễn Phí")
        cls.vip = make_movie("Phim VIP", access=Movie.Access.VIP)
        cls.film = make_movie("Phim Lẻ", kind=Movie.Kind.MOVIE, duration_minutes=90)

    def test_free_series_episode(self):
        response = self.client.get(reverse("player:watch", args=[self.free.slug, 2]))
        self.assertContains(response, "Tập 2")

    def test_movie_url_has_no_episode(self):
        self.assertEqual(self.film.get_watch_url(), f"/xem/{self.film.slug}/")
        self.assertEqual(self.client.get(self.film.get_watch_url()).status_code, 200)

    def test_vip_title_redirects_free_users_to_plans(self):
        response = self.client.get(reverse("player:watch", args=[self.vip.slug, 1]))
        self.assertRedirects(response, reverse("billing:plans"))

    def test_missing_episode_is_404(self):
        response = self.client.get(reverse("player:watch", args=[self.free.slug, 99]))
        self.assertEqual(response.status_code, 404)
