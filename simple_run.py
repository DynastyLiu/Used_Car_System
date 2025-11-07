#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版启动脚本 - 直接启动Django服务器并自动打开浏览器
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

# 修复Windows中文显示
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

# 获取虚拟环境的Python路径
if sys.platform == 'win32':
    venv_python = PROJECT_DIR / "venv" / "Scripts" / "python.exe"
else:
    venv_python = PROJECT_DIR / "venv" / "bin" / "python"

print()
print("=" * 60)
print("  🚗 二手车集市 - 开发服务器")
print("=" * 60)
print()

# 检查虚拟环境
if not venv_python.exists():
    print("❌ 虚拟环境不存在！")
    print()
    print("请先运行: 启动.bat")
    sys.exit(1)

print("✓ 虚拟环境已就绪")
print("✓ 正在启动服务器...")
print()
print("访问地址: http://127.0.0.1:5000/")
print("按 Ctrl+C 停止服务器")
print()

# 定义自动打开浏览器的函数
def open_browser():
    """等待服务器启动后自动打开浏览器"""
    time.sleep(3)  # 等待3秒让服务器启动
    url = "http://127.0.0.1:5000/"
    try:
        print()
        print("🌐 自动打开浏览器...")
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠ 无法自动打开浏览器: {e}")
        print(f"📱 请手动打开: {url}")

# 启动浏览器线程（后台运行，不阻塞服务器）
browser_thread = threading.Thread(target=open_browser, daemon=True)
browser_thread.start()

print("=" * 60)
print("  实时运行日志")
print("=" * 60)
print()

# 直接启动服务器（不捕获输出，显示实时日志）
try:
    subprocess.run([
        str(venv_python),
        "manage.py",
        "runserver",
        "127.0.0.1:5000",
        "--verbosity", "2"
    ])
except KeyboardInterrupt:
    print()
    print()
    print("=" * 60)
    print("  服务器已停止")
    print("=" * 60)
    print()
    print("感谢使用！再见！👋")
    print()
