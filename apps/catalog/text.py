import unicodedata

from django.utils.text import slugify


def normalize_vi(text: str) -> str:
    """Lowercase and strip Vietnamese diacritics: "Hậu Duệ" -> "hau due"."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().strip()


def slugify_vi(text: str) -> str:
    return slugify(normalize_vi(text))
