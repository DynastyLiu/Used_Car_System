@echo off
echo ======================================
echo    ��手车管理系统重置脚本
echo ======================================
echo.

:: 确认重置
choice /c yn /m "警告: 此操作将删除所有数据，是否继续?"
if errorlevel 2 exit /b 0

echo [1/3] 停止可能运行的服务...
taskkill /f /im python.exe >nul 2>&1

echo [2/3] 重置数据库...
call venv\Scripts\activate.bat
python manage.py migrate --fake usedcar_system zero
python manage.py flush --noinput
python manage.py migrate

echo [3/3] 重新初始化数据...
call setup.bat

echo.
echo ======================================
echo    重置完成！
echo ======================================
echo.
pause