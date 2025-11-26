"""PVE模块URL路由。"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PVEServerViewSet,
    VirtualMachineViewSet,
    console_iframe_view,
    console_asset_view,
)

router = DefaultRouter()
router.register(r'servers', PVEServerViewSet, basename='pve-server')
router.register(r'virtual-machines', VirtualMachineViewSet, basename='virtual-machine')

urlpatterns = [
    path('', include(router.urls)),
    path('console/view/', console_iframe_view, name='pve-console-view'),
    path('console/assets/<path:path>', console_asset_view, name='pve-console-asset'),
]

