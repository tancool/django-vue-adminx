"""RBAC 视图集。

提供各模型的标准 CRUD；支持过滤、搜索与排序。
默认权限使用 IsAuthenticated，如需匿名访问可在 settings 中调整 DRF 默认权限。
"""

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Menu, Permission, Role, UserRole, Organization, UserOrganization
from .serializers import (
    MenuSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserRoleSerializer,
    OrganizationSerializer,
    UserOrganizationSerializer,
)


class DefaultPermission(permissions.IsAuthenticated):
    """默认认证权限：要求登录。"""
    pass


class MenuViewSet(viewsets.ModelViewSet):
    """菜单 CRUD 与列表检索。"""
    queryset = Menu.objects.all().order_by('order', 'id')
    serializer_class = MenuSerializer
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_hidden']
    search_fields = ['title', 'path', 'component']
    ordering_fields = ['order', 'id', 'title']


class PermissionViewSet(viewsets.ModelViewSet):
    """权限 CRUD 与列表检索。"""
    queryset = Permission.objects.all().order_by('id')
    serializer_class = PermissionSerializer
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['http_method', 'menu', 'is_active']
    search_fields = ['name', 'code', 'url_pattern']
    ordering_fields = ['id', 'code', 'name']


class RoleViewSet(viewsets.ModelViewSet):
    """角色 CRUD 与列表检索，支持 data_scope 与自定义组织集合。"""
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['data_scope']
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class UserRoleViewSet(viewsets.ModelViewSet):
    """用户-角色绑定 CRUD 与列表检索。"""
    queryset = UserRole.objects.all().order_by('-created_at')
    serializer_class = UserRoleSerializer
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'role']
    search_fields = ['user__username', 'role__name']
    ordering_fields = ['created_at', 'id']


class OrganizationViewSet(viewsets.ModelViewSet):
    """组织 CRUD 与列表检索。"""
    queryset = Organization.objects.all().order_by('order', 'id')
    serializer_class = OrganizationSerializer
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'id', 'name']


class UserOrganizationViewSet(viewsets.ModelViewSet):
    """用户-组织绑定 CRUD 与列表检索。"""
    queryset = UserOrganization.objects.all().order_by('-created_at')
    serializer_class = UserOrganizationSerializer
    permission_classes = [DefaultPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'is_primary']
    search_fields = ['user__username', 'organization__name']
    ordering_fields = ['created_at', 'id']

