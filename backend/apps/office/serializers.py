"""在线文档序列化器。"""

from apps.common.serializers import BaseModelSerializer
from apps.rbac.serializers import OrganizationSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Document

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    """简单用户序列化器：只返回用户名。"""

    class Meta:
        model = User
        fields = ['id', 'username']


class DocumentListSerializer(BaseModelSerializer):
    """文档列表序列化器。"""

    owner_organization = OrganizationSerializer(read_only=True)
    created_by = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'is_pinned',
            'owner_organization',
            'created_at',
            'created_by',
            'updated_at',
        ]


class DocumentDetailSerializer(BaseModelSerializer):
    """文档详情序列化器。"""

    owner_organization = OrganizationSerializer(read_only=True)
    created_by = SimpleUserSerializer(read_only=True)
    updated_by = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']


class DocumentCreateSerializer(BaseModelSerializer):
    """文档创建序列化器。"""

    class Meta:
        model = Document
        fields = ['title', 'content', 'is_pinned', 'owner_organization', 'remark']


class DocumentUpdateSerializer(BaseModelSerializer):
    """文档更新序列化器。"""

    class Meta:
        model = Document
        fields = ['title', 'content', 'is_pinned', 'owner_organization', 'remark']



