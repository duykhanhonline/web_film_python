from django import template

from apps.ads.models import Creative
from apps.ads.slots import SLOT_SIZES
from apps.billing.tier import VIP

register = template.Library()


@register.inclusion_tag("includes/ad_slot.html", takes_context=True)
def ad_slot(context, code: str) -> dict:
    """{% ad_slot "ad-billboard" %}. Renders nothing for VIP users."""
    if code not in SLOT_SIZES:
        raise template.TemplateSyntaxError(f"Unknown ad slot: {code}")
    if context.get("user_tier") == VIP:
        return {"show": False}
    creative = Creative.objects.active().filter(slot__code=code).order_by("?").first()
    return {"show": True, "code": code, "size": SLOT_SIZES[code], "creative": creative}
