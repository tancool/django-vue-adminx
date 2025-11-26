"""PVE控制台WebSocket代理：将浏览器的noVNC流量转发到PVE。"""

import asyncio
import logging
import ssl
from urllib.parse import parse_qs

import websockets
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from .models import VirtualMachine

logger = logging.getLogger(__name__)

SESSION_CACHE_PREFIX = "pve_console_session:"
SESSION_CACHE_TTL = 60  # 秒


class PVEConsoleConsumer(AsyncWebsocketConsumer):
    """代理浏览器与PVE之间的VNC WebSocket流量。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vm = None
        self.session_data = None
        self.pve_ws = None
        self.pve_to_client_task = None

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            logger.warning("PVEConsoleConsumer: unauthenticated user, closing")
            await self.close()
            return

        self.vmid = self.scope["url_route"]["kwargs"].get("vm_id")
        token = self._get_query_token()
        if not token:
            logger.warning("PVEConsoleConsumer: missing token")
            await self.close()
            return

        cache_key = SESSION_CACHE_PREFIX + token
        session = cache.get(cache_key)
        cache.delete(cache_key)
        if not session:
            logger.warning("PVEConsoleConsumer: session not found or expired")
            await self.close()
            return

        websocket_url = session.get("websocket_url")
        if not websocket_url:
            logger.error("PVEConsoleConsumer: websocket_url missing in session data")
            await self.close()
            return

        vm = await self._get_vm()
        if not vm:
            logger.error("PVEConsoleConsumer: VM not found for id %s", self.vmid)
            await self.close()
            return

        tls_context = ssl.create_default_context()
        tls_context.check_hostname = False
        tls_context.verify_mode = ssl.CERT_NONE

        try:
            extra_headers = {}
            origin = session.get('origin')
            if origin:
                extra_headers['Origin'] = origin
            # 使用与REST相同的Token认证头，避免需要PVEAuthCookie
            if vm.server and vm.server.token_id and vm.server.token_secret:
                extra_headers['Authorization'] = f'PVEAPIToken={vm.server.token_id}={vm.server.token_secret}'

            self.pve_ws = await websockets.connect(
                websocket_url,
                ssl=tls_context,
                max_size=None,
                ping_interval=None,
                extra_headers=extra_headers or None,
                subprotocols=['binary'],
            )
        except Exception as e:
            logger.exception("PVEConsoleConsumer: failed to connect to PVE VNC websocket: %s", e)
            await self.close()
            return

        await self.accept()
        self.pve_to_client_task = asyncio.create_task(self._relay_from_pve())

    async def disconnect(self, close_code):
        if self.pve_to_client_task:
            self.pve_to_client_task.cancel()
        if self.pve_ws:
            try:
                await self.pve_ws.close()
            except Exception:
                pass
            self.pve_ws = None

    async def receive(self, text_data=None, bytes_data=None):
        if not self.pve_ws:
            return
        try:
            if bytes_data is not None:
                await self.pve_ws.send(bytes_data)
            elif text_data is not None:
                await self.pve_ws.send(text_data)
        except websockets.ConnectionClosed:
            logger.info("PVEConsoleConsumer: connection to PVE closed while sending, closing client ws")
            await self.close()

    async def _relay_from_pve(self):
        try:
            async for message in self.pve_ws:
                if isinstance(message, (bytes, bytearray)):
                    await self.send(bytes_data=message)
                else:
                    await self.send(text_data=message)
        except websockets.ConnectionClosed:
            logger.info("PVEConsoleConsumer: PVE websocket closed")
        finally:
            await self.close()

    def _get_query_token(self):
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        tokens = params.get("token")
        return tokens[0] if tokens else None

    @database_sync_to_async
    def _get_vm(self):
        try:
            return VirtualMachine.objects.select_related("server").get(pk=self.vmid)
        except VirtualMachine.DoesNotExist:
            return None

