from django.urls import re_path

from .consumers import PVEConsoleConsumer

websocket_urlpatterns = [
    re_path(r'^ws/pve/console/(?P<vm_id>\d+)/$', PVEConsoleConsumer.as_asgi()),
]

