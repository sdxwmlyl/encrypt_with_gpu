@echo off
chcp 65001 >nul
echo ==========================================
echo 源代码加密系统
echo ==========================================
echo.

:: 检查Python
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.10+
    exit /b 1
)
echo ✓ Python已安装

:: 检查Node.js
echo.
echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    exit /b 1
)
echo ✓ Node.js已安装

:: 安装后端依赖
echo.
echo 安装后端依赖...
cd src\platform\backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo 错误: 后端依赖安装失败
    exit /b 1
)
echo ✓ 后端依赖安装完成

:: 安装前端依赖
echo.
echo 安装前端依赖...
cd ..\frontend
call npm install -q
if errorlevel 1 (
    echo 错误: 前端依赖安装失败
    exit /b 1
)
echo ✓ 前端依赖安装完成

cd ..\..\..

echo.
echo ==========================================
echo 启动加密平台
echo ==========================================
echo.

:: 启动后端（新开窗口）
echo 启动后端服务...
start "加密平台后端" cmd /k "cd src\platform\backend && python main.py"
echo ✓ 后端已启动

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
echo.
echo 启动前端服务...
start "加密平台前端" cmd /k "cd src\platform\frontend && npm run dev"
echo ✓ 前端已启动

echo.
echo ==========================================
echo 加密平台已启动
echo ==========================================
echo.
echo 访问地址: http://localhost:5173
echo 后端API: http://localhost:8000
echo.
echo 关闭两个命令行窗口即可停止服务
echo.

pause
