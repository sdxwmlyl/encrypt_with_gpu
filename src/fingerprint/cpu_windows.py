"""
Windows CPU ID 采集模块
用于获取 Windows 系统的 CPU 唯一标识
"""

import subprocess
import hashlib
import re
import platform


def get_windows_cpu_id() -> str:
    """
    获取 Windows 系统的 CPU ID
    
    首先尝试使用 wmic 命令获取 ProcessorId
    如果失败，则使用 CPU Name + NumberOfCores + MaxClockSpeed 组合哈希作为备用方案
    
    Returns:
        str: 32位十六进制字符串表示的CPU指纹
    """
    # 首先尝试获取 ProcessorId
    processor_id = _get_processor_id_wmic()
    
    if processor_id:
        # 使用 ProcessorId 生成哈希
        return _hash_to_hex32(processor_id)
    
    # 备用方案：使用 CPU 属性组合
    cpu_info = _get_cpu_info_fallback()
    if cpu_info:
        return _hash_to_hex32(cpu_info)
    
    # 最终备用：使用平台信息
    fallback_data = f"{platform.machine()}-{platform.processor()}-{platform.node()}"
    return _hash_to_hex32(fallback_data)


def _get_processor_id_wmic() -> str | None:
    """
    使用 wmic 命令获取 CPU ProcessorId
    
    Returns:
        str | None: 获取到的 ProcessorId 或 None
    """
    try:
        # 使用 wmic 获取 ProcessorId
        result = subprocess.run(
            ["wmic", "cpu", "get", "ProcessorId", "/value"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # 解析输出格式 "ProcessorId=XXXXXXX"
            match = re.search(r'ProcessorId=([\w\d]+)', output, re.IGNORECASE)
            if match:
                processor_id = match.group(1).strip()
                if processor_id and processor_id != 'None':
                    return processor_id
        
        return None
    except Exception:
        return None


def _get_cpu_info_fallback() -> str | None:
    """
    备用方案：获取 CPU Name、NumberOfCores 和 MaxClockSpeed
    
    Returns:
        str | None: 组合后的CPU信息字符串或 None
    """
    try:
        # 获取 CPU Name
        name_result = subprocess.run(
            ["wmic", "cpu", "get", "Name", "/value"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        # 获取核心数
        cores_result = subprocess.run(
            ["wmic", "cpu", "get", "NumberOfCores", "/value"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        # 获取最大频率
        speed_result = subprocess.run(
            ["wmic", "cpu", "get", "MaxClockSpeed", "/value"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        cpu_parts = []
        
        # 解析 Name
        if name_result.returncode == 0:
            match = re.search(r'Name=([\w\s\-@().]+)', name_result.stdout, re.IGNORECASE)
            if match:
                cpu_parts.append(match.group(1).strip())
        
        # 解析 NumberOfCores
        if cores_result.returncode == 0:
            match = re.search(r'NumberOfCores=(\d+)', cores_result.stdout, re.IGNORECASE)
            if match:
                cpu_parts.append(f"Cores:{match.group(1)}")
        
        # 解析 MaxClockSpeed
        if speed_result.returncode == 0:
            match = re.search(r'MaxClockSpeed=(\d+)', speed_result.stdout, re.IGNORECASE)
            if match:
                cpu_parts.append(f"Speed:{match.group(1)}")
        
        if cpu_parts:
            return "|".join(cpu_parts)
        
        return None
    except Exception:
        return None


def _hash_to_hex32(data: str) -> str:
    """
    将字符串转换为32位十六进制哈希
    
    Args:
        data: 输入字符串
        
    Returns:
        str: 32位十六进制字符串（64个字符）
    """
    # 使用 SHA-256 生成哈希
    hash_obj = hashlib.sha256(data.encode('utf-8'))
    return hash_obj.hexdigest()


# 兼容性别名
get_cpu_id = get_windows_cpu_id


if __name__ == "__main__":
    # 测试代码
    cpu_id = get_windows_cpu_id()
    print(f"Windows CPU ID: {cpu_id}")
    print(f"Length: {len(cpu_id)} characters")
