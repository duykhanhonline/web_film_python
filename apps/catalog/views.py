from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, resolve_url
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from apps.billing.tier import VIP, get_user_tier
from apps.player.progress import continue_watching

from .home import cached_home
from .models import Country, Genre, Movie, MyListItem

PAGE_SIZE = 24


def my_list_ids(request: HttpRequest) -> set[int]:
    if not request.user.is_authenticated:
        return set()
    return set(MyListItem.objects.filter(user=request.user).values_list("movie_id", flat=True))


class HomeView(TemplateView):
    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home = cached_home()
        is_vip = get_user_tier(self.request) == VIP
        context.update(
            banners=[b for b in home["banners"] if not (is_vip and b.is_sponsored)],
            rows=home["rows"],
            sponsored_row=None if is_vip else home["sponsored_row"],
            continue_row=continue_watching(self.request.user),
            my_list_ids=my_list_ids(self.request),
        )
        return context


class _MovieGridView(ListView):
    template_name = "catalog/listing.html"
    context_object_name = "movies"
    paginate_by = PAGE_SIZE
    heading = ""

    def get_context_data(self, **kwargs):
        return super().get_context_data(heading=self.heading, **kwargs)


class SeriesListView(_MovieGridView):
    heading = "Phim bộ"
    queryset = Movie.objects.new_episodes()


class MovieListView(_MovieGridView):
    heading = "Phim lẻ"
    queryset = Movie.objects.movies().for_cards().order_by("-year", "-created_at")


class SearchView(_MovieGridView):
    template_name = "catalog/search.html"

    KIND_PARAMS = {"phim-bo": Movie.Kind.SERIES, "phim-le": Movie.Kind.MOVIE}
    AUDIO_PARAMS = {
        "vietsub": "has_vietsub",
        "thuyet-minh": "has_thuyet_minh",
        "long-tieng": "has_long_tieng",
    }

    # GET param -> key used in the template and below
    PARAMS = {
        "q": "q",
        "loai": "kind",
        "quoc-gia": "country",
        "the-loai": "genre",
        "nam": "year",
        "am-thanh": "audio",
    }

    def get_filters(self) -> dict[str, str]:
        params = self.request.GET
        return {key: params.get(param, "").strip()[:100] for param, key in self.PARAMS.items()}

    def get_queryset(self):
        f = self.filters = self.get_filters()
        qs = Movie.objects.search(f["q"])
        if f["kind"] in self.KIND_PARAMS:
            qs = qs.filter(kind=self.KIND_PARAMS[f["kind"]])
        if f["country"]:
            qs = qs.filter(country__slug=f["country"])
        if f["genre"]:
            qs = qs.filter(genres__slug=f["genre"])
        if f["year"].isdigit():
            qs = qs.filter(year=int(f["year"]))
        if f["audio"] in self.AUDIO_PARAMS:
            qs = qs.filter(**{self.AUDIO_PARAMS[f["audio"]]: True})
        return qs.for_cards().trending()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.filters
        querystring = self.request.GET.copy()
        querystring.pop("page", None)
        context.update(
            filters=filters,
            has_query=any(filters.values()),
            querystring=querystring.urlencode(),
            countries=Country.objects.all(),
            genres=Genre.objects.all(),
            years=Movie.objects.order_by("-year").values_list("year", flat=True).distinct(),
            kind_options=[("phim-bo", "Phim bộ"), ("phim-le", "Phim lẻ")],
            audio_options=[
                ("vietsub", "Vietsub"),
                ("thuyet-minh", "Thuyết minh"),
                ("long-tieng", "Lồng tiếng"),
            ],
        )
        if not context["has_query"]:
            context["popular"] = Movie.objects.trending().only("title")[:8]
        return context


class MovieDetailView(DetailView):
    template_name = "catalog/detail.html"
    context_object_name = "movie"

    def get_queryset(self):
        return Movie.objects.for_cards()

    def get_context_data(self, **kwargs):
        return super().get_context_data(my_list_ids=my_list_ids(self.request), **kwargs)


@require_POST
def toggle_my_list(request: HttpRequest, slug: str) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"login_url": resolve_url(settings.LOGIN_URL)}, status=401)
    movie = get_object_or_404(Movie, slug=slug)
    item, created = MyListItem.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        item.delete()
    return JsonResponse({"in_list": created})
