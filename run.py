#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
二手车管理系统启动脚本
支持5000端口，显示详细日志，方便调试和修改bug
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

# 修复Windows命令行中文显示问题
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取项目根目录
PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

def print_header(message):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {message}")
    print("=" * 50 + "\n")

def print_success(message):
    """打印成功消息"""
    print(f"✓ {message}")

def print_error(message):
    """打印错误消息"""
    print(f"✗ 错误: {message}")
    sys.exit(1)

def print_info(message):
    """打印信息"""
    print(f"ℹ {message}")

def check_python():
    """检查Python版本"""
    print_info("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python版本过低: {version.major}.{version.minor}，需要3.9+")
    print_success(f"Python版本: {version.major}.{version.minor}.{version.micro}")

def check_virtualenv():
    """检查虚拟环境"""
    print_info("检查虚拟环境...")
    venv_path = PROJECT_DIR / "venv"

    if not venv_path.exists():
        print_info("虚拟环境不存在，正在创建...")
        result = subprocess.run([sys.executable, "-m", "venv", "venv"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print_error("虚拟环境创建失败")
        print_success("虚拟环境创建完成")
    else:
        print_success("虚拟环境已存在")

def install_requirements():
    """安装依赖"""
    print_info("检查并安装依赖...")
    requirements_file = PROJECT_DIR / "requirements.txt"

    if not requirements_file.exists():
        print_error("requirements.txt不存在")

    # 使用虚拟环境的pip - 使用完整路径
    if os.name == 'nt':  # Windows
        pip_path = str(PROJECT_DIR / "venv" / "Scripts" / "pip.exe")
    else:  # Linux/Mac
        pip_path = str(PROJECT_DIR / "venv" / "bin" / "pip")

    result = subprocess.run([pip_path, "install", "-r", "requirements.txt"],
                          capture_output=True, text=True, cwd=str(PROJECT_DIR))

    if result.returncode != 0:
        print_info("警告: 部分依赖安装出现问题，但继续启动...")
        if "error" in result.stderr.lower():
            print_info(f"错误信息: {result.stderr[:200]}")
    else:
        print_success("依赖安装完成")

def check_database():
    """检查数据库"""
    print_info("检查数据库...")

    # 运行迁移 - 使用完整路径
    if os.name == 'nt':  # Windows
        python_path = str(PROJECT_DIR / "venv" / "Scripts" / "python.exe")
    else:  # Linux/Mac
        python_path = str(PROJECT_DIR / "venv" / "bin" / "python")

    result = subprocess.run([python_path, "manage.py", "migrate", "--noinput"],
                          capture_output=True, text=True, cwd=str(PROJECT_DIR))

    if result.returncode == 0:
        print_success("数据库检查完成")
    else:
        print_info("警告: 数据库迁移出现问题")

def print_welcome():
    """打印欢迎信息"""
    print_header("🚗 二手车集市 - 开发服务器")
    print("""
╔════════════════════════════════════════════════════╗
║                 服务器即将启动                    ║
║                                                  ║
║  访问地址: http://127.0.0.1:5000/                ║
║  端口: 5000                                       ║
║  环境: 开发模式（DEBUG=True）                    ║
║                                                  ║
║  快捷链接:                                        ║
║  • 首页         http://127.0.0.1:5000/           ║
║  • 管理后台     http://127.0.0.1:5000/admin/     ║
║  • API文档     http://127.0.0.1:5000/api/docs/   ║
║                                                  ║
║  操作说明:                                        ║
║  • 按 Ctrl+C 停止服务器                          ║
║  • 修改代码后自动重新加载                         ║
║  • 所有日志输出在下方显示                         ║
║  • 浏览器将自动打开系统首页                       ║
║                                                  ║
╚════════════════════════════════════════════════════╝
    """)

def print_divider():
    """打印分隔线"""
    print("\n" + "=" * 50)
    print("  实时运行日志")
    print("=" * 50 + "\n")

def open_browser():
    """打开浏览器的后台线程"""
    time.sleep(3)  # 等待3秒让服务器启动
    url = "http://127.0.0.1:5000/"
    try:
        print()
        print("🌐 自动打开浏览器...")
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠ 无法自动打开浏览器: {e}")
        print(f"📱 请手动打开: {url}")

def start_server():
    """启动Django服务器"""
    # 使用完整路径
    if os.name == 'nt':  # Windows
        python_path = str(PROJECT_DIR / "venv" / "Scripts" / "python.exe")
    else:  # Linux/Mac
        python_path = str(PROJECT_DIR / "venv" / "bin" / "python")

    # 启动浏览器线程（后台运行，不阻塞服务器）
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # 启动服务器并显示日志
    try:
        cmd = [python_path, "manage.py", "runserver", "127.0.0.1:5000", "--verbosity", "2"]
        print(f"执行命令: {' '.join(cmd)}\n")

        # 直接运行，不捕获输出，这样可以看到实时日志
        subprocess.run(cmd, cwd=str(PROJECT_DIR))
    except KeyboardInterrupt:
        print_header("服务器已停止")
        print_info("感谢使用！再见")
    except Exception as e:
        print_error(f"启动服务器失败: {e}")

def main():
    """主函数"""
    try:
        # 检查环境
        check_python()
        check_virtualenv()
        install_requirements()
        check_database()

        # 打印欢迎信息
        print_welcome()
        print_divider()

        # 启动服务器
        start_server()

    except KeyboardInterrupt:
        print_header("用户中止")
    except Exception as e:
        print_error(f"发生错误: {e}")

if __name__ == "__main__":
    main()