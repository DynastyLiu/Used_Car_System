@echo off
echo ======================================
echo    ��手车管理系统初始化脚本
echo ======================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python 3.9+已安装并添加到PATH
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)

echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)

echo [3/5] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)

echo [4/5] 执行数据库迁移...
python manage.py migrate
if errorlevel 1 (
    echo 错误: 数据库迁移失败
    pause
    exit /b 1
)

echo [5/5] 创建初始数据...
echo 正在创建车辆品牌和类型初始数据...

python manage.py shell << EOF
from vehicles.models import CarBrand, CarType

# 创建品牌
brands = [
    ("Toyota", "日本"),
    ("Honda", "日本"),
    ("Mercedes-Benz", "德国"),
    ("BMW", "德国"),
    ("Audi", "德国"),
    ("Volkswagen", "德国"),
    ("Ford", "美国"),
    ("Chevrolet", "美国"),
    ("Tesla", "美国"),
    ("Nissan", "日本"),
    ("Hyundai", "韩国"),
    ("Kia", "韩国"),
    ("Lexus", "日本"),
    ("Infiniti", "日本"),
    ("Mazda", "日本"),
    ("Subaru", "日本"),
    ("Mitsubishi", "日本"),
]

for name, country in brands:
    CarBrand.objects.get_or_create(name=name, defaults={'country': country})

# 创建车型
types = [
    ("轿车", "Sedan"),
    ("SUV", "SUV"),
    ("跑车", "Coupe"),
    ("敞篷车", "Convertible"),
    ("MPV", "MPV"),
    ("皮卡", "Pickup"),
    ("面包车", "Van"),
    ("越野车", "Off-road"),
]

for name, eng_name in types:
    CarType.objects.get_or_create(name=name, defaults={'eng_name': eng_name})

print(f"成功创建 {CarBrand.objects.count()} 个品牌")
print(f"成功创建 {CarType.objects.count()} 个车型")
EOF

echo.
echo ======================================
echo    初始化完成！
echo ======================================
echo.
echo 系统已准备好启动
echo 运行 start.bat 启动服务器
echo.
pause