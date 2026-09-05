from fastapi import UploadFile

from app.core.exceptions import InvalidImageError

ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def validate_image(image: UploadFile) -> None:
    if image.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise InvalidImageError("Only JPEG, PNG and WebP images are allowed.")


def get_image_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        raise InvalidImageError("Image must have a valid file extension.")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise InvalidImageError("Unsupported image extension.")

    return "jpg" if extension == "jpeg" else extension