from django import template
from django.db.models.fields.files import FieldFile

from apps.catalog import images

register = template.Library()

WIDTHS = {"poster": images.POSTER_WIDTHS, "backdrop": images.BACKDROP_WIDTHS}


@register.filter
def srcset(field: FieldFile, kind: str) -> str:
    """{{ movie.poster|srcset:"poster" }} -> "…_w200.webp 200w, …_w400.webp 400w"."""
    return images.srcset(field, WIDTHS[kind])


@register.filter
def rendition(field: FieldFile, width: int) -> str:
    """URL of one WebP rendition: {{ movie.backdrop|rendition:640 }}."""
    if not field:
        return ""
    return field.storage.url(images.rendition_name(field.name, int(width)))


@register.filter
def clock(seconds: int) -> str:
    """3930 -> "1:05:30", 724 -> "12:04"."""
    seconds = max(0, int(seconds or 0))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02}:{secs:02}" if hours else f"{minutes}:{secs:02}"


@register.filter
def remaining(seconds: int) -> str:
    """Time left in Vietnamese: "Còn 1 giờ 5 phút", "Còn 12 phút"."""
    minutes = max(1, round(int(seconds or 0) / 60))
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"Còn {hours} giờ {minutes} phút" if minutes else f"Còn {hours} giờ"
    return f"Còn {minutes} phút"
