@echo off
REM 黄金交易 Agent - Windows 启动脚本

echo ======================================
echo   黄金交易 Agent - 启动
echo ======================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.10 或更高版本
    pause
    exit /b 1
)

REM 创建虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装 Python 依赖
echo 📥 检查 Python 依赖...
pip install -q -r requirements.txt

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Node.js
    echo 请先安装 Node.js 18 或更高版本
    pause
    exit /b 1
)

REM 安装前端依赖
if not exist "frontend\node_modules" (
    echo 📥 安装前端依赖...
    cd frontend
    npm install
    cd ..
)

echo.
echo ======================================
echo   启动服务
echo ======================================
echo.

REM 启动后端
echo 🚀 启动后端服务 (http://127.0.0.1:8000)...
start "Gold Trading Backend" cmd /k "cd backend && python main.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🚀 启动前端服务 (http://localhost:5173)...
cd frontend
start "Gold Trading Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ======================================
echo   ✅ 服务已启动
echo ======================================
echo.
echo 后端: http://127.0.0.1:8000
echo 前端: http://localhost:5173
echo API 文档: http://127.0.0.1:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
