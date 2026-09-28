from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

from apps.billing.tier import get_user_tier
from apps.catalog.models import Country, Genre


def _nav_menus() -> dict:
    return {
        "countries": list(Country.objects.all()),
        "genres": list(Genre.objects.all()),
    }


def site(request: HttpRequest) -> dict:
    return {
        "brand_name": settings.BRAND_NAME,
        "user_tier": get_user_tier(request),
        "nav_menus": cache.get_or_set("nav_menus", _nav_menus, settings.HOME_CACHE_SECONDS),
    }
