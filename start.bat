@echo off
echo ======================================
echo    ��手车管理系统启动脚本
echo ======================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python 3.9+已安装并添加到PATH
    pause
    exit /b 1
)

echo [1/6] 检查虚拟环境...
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)

echo [2/6] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)

echo [3/6] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)

echo [4/6] 检查MySQL数据库连接...
python -c "import pymysql; pymysql.connect(host='localhost', user='root', password='123456')" >nul 2>&1
if errorlevel 1 (
    echo 警告: 无法连接到MySQL数据库
    echo 请确保MySQL服务已启动，数据库配置如下:
    echo   主机: localhost
    echo   端口: 3306
    echo   用户: root
    echo   密码: 123456
    echo   数据库名: used_car_system
    echo.
    echo 请手动创建数据库:
    echo   CREATE DATABASE used_car_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    echo.
    choice /c yn /m "是否继续运行?(y=继续,n=退出)"
    if errorlevel 2 exit /b 1
)

echo [5/6] 执行数据库迁移...
python manage.py migrate
if errorlevel 1 (
    echo 错误: 数据库迁移失败
    pause
    exit /b 1
)

echo [6/6] 创建超级用户...
echo 请按提示输入管理员账户信息...
echo (如果已存在管理员账户，按Ctrl+C跳过)
echo.
python manage.py createsuperuser
if errorlevel 1 (
    echo 警告: 超级用户创建可能失败或已跳过
)

echo.
echo ======================================
echo    启动完成！服务器即将启动
echo ======================================
echo.
echo 访问地址:
echo   前端界面: http://localhost:8000/
echo   后台管理: http://localhost:8000/admin/
echo   API文档: http://localhost:8000/api/docs/
echo.
echo 按 Ctrl+C 停止服务器
echo ======================================
echo.

python manage.py runserver