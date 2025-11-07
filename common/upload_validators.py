from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image

def validate_image(file):
    """校验图片大小与格式。超限或格式不允许则抛出 ValidationError。"""
    # 大小校验
    max_bytes = settings.MEDIA_MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(f"图片大小超过限制：{settings.MEDIA_MAX_IMAGE_SIZE_MB}MB")
    # 格式校验
    try:
        img = Image.open(file)
        fmt = img.format.upper()
        allowed = {f.strip().upper() for f in settings.ALLOWED_IMAGE_FORMATS}
        if fmt not in allowed:
            raise ValidationError(f"不支持的图片格式：{fmt}，仅支持：{', '.join(sorted(allowed))}")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("无法识别的图片文件") from e
