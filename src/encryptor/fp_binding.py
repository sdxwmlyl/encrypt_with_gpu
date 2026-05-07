#!/usr/bin/env python3
"""
指纹绑定嵌入模块
生成可在被加密项目中运行的校验代码
"""

import hashlib
import base64
from datetime import datetime
from typing import Dict, Any


def generate_protection_code(fingerprint_hash: str, expiry_date: str) -> str:
    """
    生成指纹绑定保护代码
    
    Args:
        fingerprint_hash: 绑定的设备指纹哈希值
        expiry_date: 有效期截止日期，格式为 "YYYY-MM-DD"
        
    Returns:
        生成的Python校验代码字符串
    """
    # 验证参数
    if not fingerprint_hash or len(fingerprint_hash) < 32:
        raise ValueError("指纹哈希无效")
    
    try:
        datetime.strptime(expiry_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"有效期格式无效，请使用 YYYY-MM-DD 格式: {expiry_date}")
    
    # 生成嵌入的校验代码
    protection_code = f'''# 自动生成的指纹绑定校验代码 - 请勿修改
import hashlib
import platform
import subprocess
from datetime import datetime

# 绑定的指纹和有效期配置
_BOUND_FINGERPRINT_HASH = "{fingerprint_hash}"
_EXPIRY_DATE = "{expiry_date}"


def _collect_device_fingerprint() -> str:
    """采集当前设备指纹"""
    components = []
    system = platform.system()
    
    try:
        if system == "Linux":
            # Linux CPU信息
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("processor") or line.startswith("model name"):
                        components.append(line.strip())
                        
            # Linux GPU信息
            try:
                result = subprocess.run(
                    ["lspci"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                for line in result.stdout.split("\\n"):
                    if "VGA" in line:
                        components.append(line.strip())
            except Exception:
                pass
                
        elif system == "Windows":
            # Windows CPU信息
            result = subprocess.run(
                ["wmic", "cpu", "get", "Name,ProcessorId", "/format:csv"],
                capture_output=True,
                text=True,
                timeout=5
            )
            components.append(result.stdout.strip())
            
            # Windows GPU信息
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "Name", "/format:csv"],
                capture_output=True,
                text=True,
                timeout=5
            )
            components.append(result.stdout.strip())
            
    except Exception as e:
        components.append(f"ERROR: {{str(e)}}")
    
    # 添加系统信息
    components.append(f"SYSTEM: {{system}}")
    components.append(f"MACHINE: {{platform.machine()}}")
    
    # 计算指纹哈希
    fingerprint_data = "|".join(components)
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()


def _verify_fingerprint() -> bool:
    """验证当前设备指纹是否与绑定指纹匹配"""
    current_fp = _collect_device_fingerprint()
    return current_fp == _BOUND_FINGERPRINT_HASH


def _verify_expiry() -> bool:
    """验证当前日期是否在有效期内"""
    try:
        expiry = datetime.strptime(_EXPIRY_DATE, "%Y-%m-%d")
        current = datetime.now()
        return current <= expiry
    except Exception:
        return False


def _check_license():
    """执行完整的许可证校验"""
    errors = []
    
    # 检查有效期
    if not _verify_expiry():
        errors.append(f"软件授权已过期 (有效期至: {{_EXPIRY_DATE}})")
    
    # 检查指纹
    if not _verify_fingerprint():
        errors.append("设备指纹不匹配，此软件未在当前设备授权")
    
    if errors:
        error_msg = "\\n".join([
            "=" * 50,
            "  软件授权验证失败",
            "=" * 50,
            *errors,
            "",
            "请联系管理员获取授权支持。",
            "=" * 50
        ])
        raise RuntimeError(error_msg)


# 在模块导入时自动执行校验
_check_license()
'''
    
    return protection_code


if __name__ == "__main__":
    # 测试
    test_fp = "a" * 64
    test_expiry = "2025-12-31"
    code = generate_protection_code(test_fp, test_expiry)
    print("生成的保护代码:")
    print(code)
