"""WebP renditions for uploaded images, used by the `srcset` template filter."""

import io
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
from PIL import Image

POSTER_WIDTHS = (200, 400)
BACKDROP_WIDTHS = (640, 1280, 1920)


def rendition_name(name: str, width: int) -> str:
    path = PurePosixPath(name)
    return str(path.with_name(f"{path.stem}_w{width}.webp"))


def make_renditions(field: FieldFile, widths: tuple[int, ...]) -> None:
    """Writes <stem>_w<width>.webp next to the original for each width."""
    if not field:
        return
    storage = field.storage
    with field.open("rb") as fh, Image.open(fh) as img:
        img = img.convert("RGB")
        for width in widths:
            name = rendition_name(field.name, width)
            if storage.exists(name):
                continue
            height = round(img.height * width / img.width)
            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            resized.save(buf, "WEBP", quality=80, method=6)
            storage.save(name, ContentFile(buf.getvalue()))


def srcset(field: FieldFile, widths: tuple[int, ...]) -> str:
    if not field:
        return ""
    storage = field.storage
    return ", ".join(f"{storage.url(rendition_name(field.name, w))} {w}w" for w in widths)
