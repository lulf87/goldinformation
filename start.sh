#!/bin/bash

# 黄金交易 Agent - 启动脚本

echo "======================================"
echo "  黄金交易 Agent - 启动"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.10 或更高版本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装 Python 依赖
echo "📥 检查 Python 依赖..."
pip install -q -r requirements.txt

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    echo "请先安装 Node.js 18 或更高版本"
    exit 1
fi

# 安装前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "======================================"
echo "  启动服务"
echo "======================================"
echo ""

# 启动后端 (后台运行)
echo "🚀 启动后端服务 (http://127.0.0.1:8000)..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端服务 (http://localhost:5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================"
echo "  ✅ 服务已启动"
echo "======================================"
echo ""
echo "后端: http://127.0.0.1:8000"
echo "前端: http://localhost:5173"
echo "API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 等待信号
wait
