from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

validate_image_extension = FileExtensionValidator(["jpg", "jpeg", "png", "webp", "avif"])


def validate_image_size(file) -> None:
    limit = settings.MAX_IMAGE_UPLOAD_BYTES
    if file.size > limit:
        raise ValidationError(f"Ảnh quá lớn. Dung lượng tối đa là {limit // (1024 * 1024)} MB.")


IMAGE_VALIDATORS = [validate_image_extension, validate_image_size]


def validate_trailer_size(file) -> None:
    limit = settings.MAX_TRAILER_UPLOAD_BYTES
    if file.size > limit:
        raise ValidationError(f"Trailer quá lớn. Dung lượng tối đa là {limit // (1024 * 1024)} MB.")


TRAILER_VALIDATORS = [FileExtensionValidator(["mp4"]), validate_trailer_size]
