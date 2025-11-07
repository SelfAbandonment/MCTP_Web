from io import BytesIO
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image
from .models import User

@receiver(pre_save, sender=User)
def convert_avatar_to_webp(sender, instance: User, **kwargs):
    """在保存用户前尝试将头像转换为 WebP（失败则保持原格式）。"""
    if instance.avatar and hasattr(instance.avatar, 'file'):
        try:
            instance.avatar.file.seek(0)
            img = Image.open(instance.avatar.file)
            if img.format != 'WEBP':
                img = img.convert('RGB')
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=85, method=6)
                buffer.seek(0)
                instance.avatar.save(
                    instance.avatar.name.rsplit('.', 1)[0] + '.webp',
                    ContentFile(buffer.read()),
                    save=False,
                )
        except Exception:
            # 转换失败则忽略
            pass
