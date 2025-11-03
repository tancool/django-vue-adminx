"""
URL configuration for django_vue_adminx project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""RBAC 路由注册。

使用 DRF DefaultRouter 自动生成标准 CRUD 路由：
 /api/rbac/<resource>/ 和 /api/rbac/<resource>/{pk}/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuViewSet,
    PermissionViewSet,
    RoleViewSet,
    UserRoleViewSet,
    OrganizationViewSet,
    UserOrganizationViewSet,
)

# 可根据需要将 basename 显式指定，当前使用默认模型名推导
router = DefaultRouter()
router.register(r'menus', MenuViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'user-organizations', UserOrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
