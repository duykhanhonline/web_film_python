from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.billing.tier import VIP, get_user_tier
from apps.catalog.models import Episode, Movie


def watch(request: HttpRequest, slug: str, number: int = 1) -> HttpResponse:
    movie = get_object_or_404(Movie, slug=slug)
    if movie.is_vip and get_user_tier(request) != VIP:
        return redirect("billing:plans")
    season_number = request.GET.get("phan", "1")
    episode = get_object_or_404(
        Episode.objects.select_related("season"),
        season__movie=movie,
        season__number=int(season_number) if season_number.isdigit() else 1,
        number=number,
    )
    return render(request, "player/watch.html", {"movie": movie, "episode": episode})
