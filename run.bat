@echo off
chcp 65001 >nul
echo.
echo ====================================
echo   二手车管理系统启动脚本
echo   端口: 5000
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保已安装Python 3.9+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo [提示] 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
)

REM 激活虚拟环境
echo [正在激活虚拟环境...]
call venv\Scripts\activate.bat

REM 安装依赖
echo [正在检查依赖...]
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，继续启动...
)

REM 数据库迁移
echo [正在检查数据库...]
python manage.py migrate --noinput >nul 2>&1

REM 显示启动信息
echo.
echo ====================================
echo   ✓ 准备完成，正在启动服务器...
echo ====================================
echo.
echo 访问地址: http://127.0.0.1:5000/
echo 按 Ctrl+C 停止服务器
echo.
echo ====================================
echo   实时运行日志
echo ====================================
echo.

REM 启动服务器，显示日志
python manage.py runserver 127.0.0.1:5000 --verbosity 2

pause