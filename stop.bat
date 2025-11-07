@echo off
echo ======================================
echo    停止二手车管理系统
echo ======================================
echo.

echo 正在停止Python服务器...
taskkill /f /im python.exe >nul 2>&1
if errorlevel 1 (
    echo 未找到正在运行的Python服务器
) else (
    echo 服务器已停止
)

echo.
echo 所有服务已停止
echo.
pause