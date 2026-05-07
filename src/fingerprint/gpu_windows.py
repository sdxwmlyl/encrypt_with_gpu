"""
Windows GPU ID 采集模块

用于采集 Windows 系统的 GPU 硬件指纹信息。
支持主方案（PNPDeviceID 提取）和备用方案（Name + AdapterRAM 哈希）。
"""

import subprocess
import re
import hashlib
import platform
from typing import Optional


def get_windows_gpu_id() -> Optional[str]:
    """
    获取 Windows 系统的 GPU ID 指纹。
    
    主方案: 使用 wmic 命令获取 PNPDeviceID，提取 PCI\VEN_xxxx&DEV_xxxx 部分
    备用方案: 使用 Name + AdapterRAM 组合哈希
    
    Returns:
        32位十六进制字符串，失败返回 None
    """
    # 首先检查是否在 Windows 系统上运行
    if platform.system() != "Windows":
        # 非 Windows 系统，返回 None 让调用方处理
        return None
    
    # 尝试主方案：获取 PNPDeviceID
    gpu_id = _get_gpu_id_from_pnp_device_id()
    if gpu_id:
        return gpu_id
    
    # 主方案失败，使用备用方案
    return _get_gpu_id_from_name_and_ram()


def _get_gpu_id_from_pnp_device_id() -> Optional[str]:
    """
    使用 wmic 命令获取 PNPDeviceID 并提取 GPU ID。
    
    命令: wmic path win32_VideoController get PNPDeviceID /value
    
    Returns:
        32位十六进制字符串，失败返回 None
    """
    try:
        # 执行 wmic 命令
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "PNPDeviceID", "/value"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            return None
        
        output = result.stdout
        
        # 查找所有 PNPDeviceID 值
        # 格式: PNPDeviceID=PCI\VEN_10DE&DEV_1F91&SUBSYS_3A5E1B4C&REV_A1\4&1D81E3C0&0&0008
        pattern = r'PNPDeviceID=([\w\\]+)'
        matches = re.findall(pattern, output)
        
        if not matches:
            return None
        
        # 提取每个 GPU 的 VEN_xxxx&DEV_xxxx 部分
        gpu_identifiers = []
        for match in matches:
            # 匹配 PCI\VEN_xxxx&DEV_xxxx 部分
            ven_dev_pattern = r'PCI\\VEN_([0-9A-Fa-f]{4})&DEV_([0-9A-Fa-f]{4})'
            ven_dev_match = re.search(ven_dev_pattern, match)
            
            if ven_dev_match:
                vendor_id = ven_dev_match.group(1).upper()
                device_id = ven_dev_match.group(2).upper()
                gpu_identifiers.append(f"{vendor_id}{device_id}")
        
        if not gpu_identifiers:
            return None
        
        # 如果有多个 GPU，按字母排序后拼接
        gpu_identifiers.sort()
        combined = "".join(gpu_identifiers)
        
        # 生成 32 位十六进制哈希
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()[:32]
        
    except Exception:
        return None


def _get_gpu_id_from_name_and_ram() -> Optional[str]:
    """
    备用方案：使用 Name + AdapterRAM 组合生成 GPU ID。
    
    命令: wmic path win32_VideoController get Name,AdapterRAM /value
    
    Returns:
        32位十六进制字符串，失败返回 None
    """
    try:
        # 获取 GPU 名称和显存信息
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM", "/value"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            return None
        
        output = result.stdout
        
        # 解析 Name 和 AdapterRAM
        gpu_entries = []
        
        # 按空行分割，每个 GPU 的信息是一段
        sections = re.split(r'\n\s*\n', output.strip())
        
        for section in sections:
            name_match = re.search(r'Name=([\w\s\-]+)', section)
            ram_match = re.search(r'AdapterRAM=(\d+)', section)
            
            if name_match and ram_match:
                name = name_match.group(1).strip()
                ram = ram_match.group(1).strip()
                gpu_entries.append(f"{name}_{ram}")
        
        if not gpu_entries:
            return None
        
        # 按字母排序后拼接
        gpu_entries.sort()
        combined = "|".join(gpu_entries)
        
        # 生成 32 位十六进制哈希
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()[:32]
        
    except Exception:
        return None


def get_gpu_info() -> dict:
    """
    获取详细的 GPU 信息（用于调试和展示）。
    
    Returns:
        包含 GPU 详细信息的字典
    """
    info = {
        "platform": platform.system(),
        "gpus": [],
        "fingerprint": None
    }
    
    if platform.system() != "Windows":
        info["error"] = "Not running on Windows"
        return info
    
    try:
        # 获取详细信息
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", 
             "Name,PNPDeviceID,AdapterRAM,DriverVersion", "/value"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            output = result.stdout
            sections = re.split(r'\n\s*\n', output.strip())
            
            for section in sections:
                gpu = {}
                
                name_match = re.search(r'Name=([\w\s\-]+)', section)
                if name_match:
                    gpu["name"] = name_match.group(1).strip()
                
                pnp_match = re.search(r'PNPDeviceID=([\w\\&]+)', section)
                if pnp_match:
                    gpu["pnp_device_id"] = pnp_match.group(1).strip()
                    # 提取 VEN/DEV
                    ven_dev_pattern = r'VEN_([0-9A-Fa-f]{4})&DEV_([0-9A-Fa-f]{4})'
                    ven_dev_match = re.search(ven_dev_pattern, gpu.get("pnp_device_id", ""))
                    if ven_dev_match:
                        gpu["vendor_id"] = ven_dev_match.group(1).upper()
                        gpu["device_id"] = ven_dev_match.group(2).upper()
                
                ram_match = re.search(r'AdapterRAM=(\d+)', section)
                if ram_match:
                    ram_bytes = int(ram_match.group(1))
                    gpu["adapter_ram_mb"] = ram_bytes // (1024 * 1024) if ram_bytes > 0 else 0
                
                driver_match = re.search(r'DriverVersion=([\d\.]+)', section)
                if driver_match:
                    gpu["driver_version"] = driver_match.group(1).strip()
                
                if gpu:
                    info["gpus"].append(gpu)
        
        # 获取指纹
        info["fingerprint"] = get_windows_gpu_id()
        
    except Exception as e:
        info["error"] = str(e)
    
    return info


# 测试代码
if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("Windows GPU ID 采集模块测试")
    print("=" * 60)
    
    if platform.system() != "Windows":
        print(f"当前平台: {platform.system()}")
        print("注意：此模块仅在 Windows 系统上可用")
        print("\n模拟测试模式 - 展示函数结构")
        print(f"get_windows_gpu_id() 在非 Windows 平台将返回: {get_windows_gpu_id()}")
    else:
        print("\n1. GPU 指纹 ID:")
        fp = get_windows_gpu_id()
        if fp:
            print(f"   {fp}")
        else:
            print("   获取失败")
        
        print("\n2. 详细 GPU 信息:")
        info = get_gpu_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
