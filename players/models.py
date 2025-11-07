from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import BaseModel

class User(AbstractUser, BaseModel):
    """自定义用户：扩展昵称、QQ、白名单标记、头像；继承 BaseModel 增加通用字段。"""
    nickname = models.CharField("游戏昵称", max_length=50, blank=True, db_index=True)
    qq = models.CharField("QQ", max_length=15, blank=True, db_index=True, unique=True, null=True)
    is_whitelisted = models.BooleanField("白名单", default=False, db_index=True)
    avatar = models.ImageField("头像", upload_to="avatars/%Y/%m/", blank=True, null=True)

    class Meta:
        verbose_name = "玩家"
        verbose_name_plural = "玩家"
        indexes = [
            models.Index(fields=["nickname"]),
            models.Index(fields=["qq"]),
            models.Index(fields=["is_whitelisted"]),
        ]

    def __str__(self):
        return self.nickname or self.username