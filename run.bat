@echo off & chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   正在启动翻译服务 ...
echo ============================================

python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [错误] 未检测到 Python，请安装 Python 并加入 PATH。
    pause
    exit /b 1
)

python main.py

echo.
echo 服务已停止，请查看上方日志。
pause