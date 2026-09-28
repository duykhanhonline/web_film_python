from django import template

register = template.Library()


@register.filter
def vnd(amount: int) -> str:
    """99000 -> "99.000 ₫" (vi-VN format, VND has no decimals)."""
    return f"{int(amount):,} ₫".replace(",", ".")
