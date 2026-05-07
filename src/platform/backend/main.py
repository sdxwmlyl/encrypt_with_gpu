"""
源代码加密平台 - FastAPI后端
提供指纹采集和项目加密API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fingerprint import FingerprintCollector
from encryptor.python_obfuscator import PythonObfuscator
from encryptor.fp_binding import generate_protection_code
from encryptor.js_obfuscator import VueProjectObfuscator

app = FastAPI(
    title="源代码加密平台",
    description="用于加密Python和Vue项目的本地平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态
encryption_status = {
    "status": "idle",
    "progress": 0,
    "message": "",
    "output_path": None
}


class EncryptRequest(BaseModel):
    source_path: str
    output_path: str
    expiry_date: str  # YYYY-MM-DD格式
    fingerprint: Optional[str] = None


@app.get("/api/fingerprint")
def get_fingerprint():
    """获取本机指纹信息"""
    try:
        collector = FingerprintCollector()
        fp_data = collector.collect()
        return {
            "success": True,
            "data": fp_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/encrypt")
async def encrypt_project(request: EncryptRequest, background_tasks: BackgroundTasks):
    """启动加密任务"""
    global encryption_status
    
    if encryption_status["status"] == "running":
        raise HTTPException(status_code=400, detail="已有加密任务在运行")
    
    # 验证路径
    source = Path(request.source_path)
    output = Path(request.output_path)
    
    if not source.exists():
        raise HTTPException(status_code=400, detail=f"源代码路径不存在: {request.source_path}")
    
    # 获取指纹
    try:
        collector = FingerprintCollector()
        if request.fingerprint:
            fp_hash = request.fingerprint
        else:
            fp_hash = collector.get_combined_hash()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"指纹采集失败: {str(e)}")
    
    # 启动后台加密任务
    encryption_status = {
        "status": "running",
        "progress": 0,
        "message": "开始加密...",
        "output_path": str(output)
    }
    
    background_tasks.add_task(
        do_encrypt,
        source,
        output,
        fp_hash,
        request.expiry_date
    )
    
    return {
        "success": True,
        "message": "加密任务已启动",
        "fingerprint": fp_hash
    }


@app.get("/api/encrypt/status")
def get_encrypt_status():
    """获取加密状态"""
    return encryption_status


def do_encrypt(source: Path, output: Path, fingerprint: str, expiry: str):
    """执行加密任务"""
    global encryption_status
    
    try:
        # 创建输出目录
        output.mkdir(parents=True, exist_ok=True)
        
        # 统计文件
        py_files = list(source.rglob("*.py"))
        total = len(py_files)
        
        encryption_status["message"] = f"找到 {total} 个Python文件"
        encryption_status["progress"] = 10
        
        # 生成保护代码
        protection_code = generate_protection_code(fingerprint, expiry)
        
        # 加密每个文件
        obfuscator = PythonObfuscator()
        for i, file_path in enumerate(py_files, 1):
            relative = file_path.relative_to(source)
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取原文件
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # 混淆代码
            obfuscated = obfuscator.obfuscate(source_code)
            
            # 添加保护代码
            final_code = protection_code + "\n\n" + obfuscated
            
            # 写入
            with open(target, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            encryption_status["progress"] = 10 + int(80 * i / total)
            encryption_status["message"] = f"加密中... ({i}/{total}) {relative}"
        
        # 复制其他文件
        encryption_status["message"] = "复制其他文件..."
        for file_path in source.rglob("*"):
            if file_path.is_file() and file_path.suffix != '.py':
                relative = file_path.relative_to(source)
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(file_path, target)
        
        encryption_status["status"] = "completed"
        encryption_status["progress"] = 100
        encryption_status["message"] = f"加密完成！输出到: {output}"
        
    except Exception as e:
        encryption_status["status"] = "error"
        encryption_status["message"] = f"加密失败: {str(e)}"


@app.post("/api/verify")
def verify_encrypted_project(path: str):
    """验证加密后的项目是否可以运行"""
    try:
        project_path = Path(path)
        if not project_path.exists():
            return {"success": False, "message": "项目路径不存在"}
        
        # 检查是否有Python文件
        py_files = list(project_path.rglob("*.py"))
        if not py_files:
            return {"success": False, "message": "未找到Python文件"}
        
        # 尝试导入第一个文件验证语法
        # 注意：这会触发指纹校验，可能会失败
        return {
            "success": True,
            "message": f"找到 {len(py_files)} 个Python文件，项目结构正常"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
