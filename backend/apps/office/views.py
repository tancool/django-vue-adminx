"""在线文档视图集。"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.data_mixins import DataScopeFilterMixin
from apps.common.mixins import AuditOwnerPopulateMixin, SoftDeleteMixin
from apps.common.viewsets import ActionSerializerMixin

from .models import Document
from .serializers import (
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
)


class DocumentViewSet(
    DataScopeFilterMixin,
    AuditOwnerPopulateMixin,
    SoftDeleteMixin,
    ActionSerializerMixin,
    viewsets.ModelViewSet,
):
    """在线文档 CRUD 视图集。"""

    queryset = (
        Document.objects.select_related(
            'owner_organization',
            'created_by',
            'updated_by',
        )
        .all()
        .order_by('-is_pinned', '-updated_at', '-id')
    )
    permission_classes = [permissions.IsAuthenticated]

    # 兜底
    serializer_class = DocumentDetailSerializer

    # 按动作切换
    list_serializer_class = DocumentListSerializer
    retrieve_serializer_class = DocumentDetailSerializer
    create_serializer_class = DocumentCreateSerializer
    update_serializer_class = DocumentUpdateSerializer
    partial_update_serializer_class = DocumentUpdateSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_pinned', 'owner_organization']
    search_fields = ['title', 'content']
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'is_pinned']

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """置顶/取消置顶文档。"""
        doc = self.get_object()
        doc.is_pinned = not doc.is_pinned
        doc.save(update_fields=['is_pinned'])
        return Response({'id': doc.id, 'is_pinned': doc.is_pinned})



