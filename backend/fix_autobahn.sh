#!/bin/bash
# 修复 autobahn C 扩展问题的脚本

echo "正在修复 autobahn C 扩展问题..."

# 设置环境变量禁用 C 扩展
export AUTOBAHN_USE_UVLOOP=0
export TWISTED_REACTOR=asyncio

# 重新安装 autobahn（使用纯 Python 版本）
pip uninstall -y autobahn
pip install --no-binary autobahn autobahn==24.4.2

echo "修复完成！请重启服务器。"
echo "如果问题仍然存在，请运行："
echo "  export AUTOBAHN_USE_UVLOOP=0"
echo "  export TWISTED_REACTOR=asyncio"
echo "  daphne -b 0.0.0.0 -p 8000 django_vue_adminx.asgi:application"

