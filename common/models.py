from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """基础抽象模型：启用、浏览量、创建/更新时间，统一索引与排序。"""
    is_active = models.BooleanField("启用", default=True, db_index=True)
    views = models.PositiveIntegerField("浏览量", default=0, db_index=True)
    created_at = models.DateTimeField("创建时间", default=timezone.now, db_index=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        get_latest_by = "创建时间"

class BaseCategory(BaseModel):
    """抽象分类：名称、短标识、父级与排序。"""
    name = models.CharField("名称", max_length=64, db_index=True)
    slug = models.SlugField("标识", max_length=100, unique=True)
    parent = models.ForeignKey("self", verbose_name="父级", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    sort_order = models.IntegerField("排序", default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sort_order"]),
        ]

    def __str__(self):
        return self.name
