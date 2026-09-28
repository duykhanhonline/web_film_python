from django.http import HttpRequest

from .models import Subscription

FREE = "free"
VIP = "vip"


def get_user_tier(request: HttpRequest) -> str:
    """ "vip" when the user has an active Subscription, else "free". Cached per request."""
    tier = getattr(request, "_user_tier", None)
    if tier is None:
        user = request.user
        is_vip = user.is_authenticated and Subscription.objects.active().filter(user=user).exists()
        tier = VIP if is_vip else FREE
        request._user_tier = tier
    return tier
