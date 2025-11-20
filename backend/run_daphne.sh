#!/bin/bash
# 启动 Daphne 服务器的脚本（修复 autobahn C 扩展问题）

# 设置环境变量禁用 C 扩展
export AUTOBAHN_USE_UVLOOP=0
export TWISTED_REACTOR=asyncio
export PYTHONUNBUFFERED=1

# 启动 Daphne
echo "启动 Daphne WebSocket 服务器..."
echo "环境变量已设置：AUTOBAHN_USE_UVLOOP=0, TWISTED_REACTOR=asyncio"

daphne -b 0.0.0.0 -p 8000 django_vue_adminx.asgi:application

