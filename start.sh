#!/bin/bash
# 源代码加密系统 - 启动脚本

echo "=========================================="
echo "源代码加密系统"
echo "=========================================="
echo ""

# 检查Python
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3.10+"
    exit 1
fi

# 检查Node.js
echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

# 安装后端依赖
echo ""
echo "安装后端依赖..."
cd src/platform/backend
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "错误: 后端依赖安装失败"
    exit 1
fi
echo "✓ 后端依赖安装完成"

# 安装前端依赖
echo ""
echo "安装前端依赖..."
cd ../frontend
npm install -q
if [ $? -ne 0 ]; then
    echo "错误: 前端依赖安装失败"
    exit 1
fi
echo "✓ 前端依赖安装完成"

cd ../../..

echo ""
echo "=========================================="
echo "启动加密平台"
echo "=========================================="
echo ""

# 启动后端（后台）
echo "启动后端服务..."
cd src/platform/backend
python3 main.py &
BACKEND_PID=$!
echo "✓ 后端已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✓ 前端已启动 (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "加密平台已启动"
echo "=========================================="
echo ""
echo "访问地址: http://localhost:5173"
echo "后端API: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
wait
