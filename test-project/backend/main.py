"""
测试后端 - FastAPI 应用
用于验证源代码加密系统的功能
"""

from fastapi import FastAPI
from datetime import datetime
import platform

app = FastAPI(title="测试后端", version="1.0.0")


@app.get("/hello")
def hello():
    """返回问候语"""
    return {
        "message": "Hello, World!",
        "timestamp": datetime.now().isoformat(),
        "service": "test-backend"
    }


@app.get("/status")
def status():
    """返回服务状态"""
    return {
        "status": "running",
        "version": "1.0.0",
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "uptime": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
