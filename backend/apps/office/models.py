"""在线文档模型（系统办公）。"""

from django.db import models
from apps.common.models import BaseAuditModel


class Document(BaseAuditModel):
    """在线文档：用于存储富文本内容，支持审计字段。"""

    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(blank=True, default='', verbose_name='内容')
    is_pinned = models.BooleanField(default=False, verbose_name='置顶')

    class Meta:
        verbose_name = '文档'
        verbose_name_plural = '文档'
        ordering = ['-is_pinned', '-updated_at', '-id']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return self.title


