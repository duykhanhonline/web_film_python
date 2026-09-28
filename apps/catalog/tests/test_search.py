from django.urls import reverse

from apps.catalog.models import Movie
from apps.catalog.text import normalize_vi, slugify_vi

from .factories import MediaTestCase, make_genre, make_movie


class NormalizeViTests(MediaTestCase):
    def test_strips_diacritics_and_d(self):
        self.assertEqual(normalize_vi("Hậu Duệ Mặt Trời"), "hau due mat troi")
        self.assertEqual(normalize_vi("  Đầu Bếp Nhà Bên "), "dau bep nha ben")

    def test_slugify_vi(self):
        self.assertEqual(slugify_vi("Đầu Bếp Nhà Bên"), "dau-bep-nha-ben")


class MovieSearchTests(MediaTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dots = make_movie("Hậu Duệ Mặt Trời", original_title="Descendants of the Sun")
        cls.other = make_movie("Mùa Hè Cuối Cùng", kind=Movie.Kind.MOVIE, duration_minutes=100)

    def test_search_text_is_saved(self):
        self.assertEqual(self.dots.search_text, "hau due mat troi descendants of the sun")

    def test_slug_is_generated_without_diacritics(self):
        self.assertEqual(self.dots.slug, "hau-due-mat-troi")

    def test_duplicate_titles_get_unique_slugs(self):
        again = make_movie("Hậu Duệ Mặt Trời")
        self.assertEqual(again.slug, "hau-due-mat-troi-2")

    def test_query_without_diacritics_matches(self):
        self.assertEqual(list(Movie.objects.search("hau due mat troi")), [self.dots])

    def test_query_with_diacritics_and_original_title_match(self):
        self.assertEqual(list(Movie.objects.search("Mặt Trời")), [self.dots])
        self.assertEqual(list(Movie.objects.search("descendants")), [self.dots])

    def test_search_page_finds_title(self):
        response = self.client.get(reverse("catalog:search"), {"q": "hau due mat troi"})
        self.assertContains(response, "Hậu Duệ Mặt Trời")
        self.assertNotContains(response, "Mùa Hè Cuối Cùng")

    def test_search_filters(self):
        url = reverse("catalog:search")
        response = self.client.get(url, {"loai": "phim-le"})
        self.assertEqual(list(response.context["movies"]), [self.other])

        make_genre("Kinh dị", "kinh-di")
        response = self.client.get(url, {"the-loai": "kinh-di"})
        self.assertEqual(list(response.context["movies"]), [])

    def test_empty_query_shows_popular_searches(self):
        response = self.client.get(reverse("catalog:search"))
        self.assertContains(response, "Tìm kiếm phổ biến")
