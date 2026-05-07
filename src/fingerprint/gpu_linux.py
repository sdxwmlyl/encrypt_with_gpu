#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux GPU ID 采集模块
用于获取 Linux 系统 GPU 设备指纹
"""

import subprocess
import re
import hashlib
import platform


def get_linux_gpu_id() -> str:
    """
    获取 Linux 系统 GPU ID
    
    策略:
    1. 首先尝试使用 lspci -v 获取 GPU 设备信息
    2. 提取 VGA compatible controller 的设备ID
    3. 备用方案: 尝试 nvidia-smi -L (NVIDIA GPU)
    4. 如果都没有，返回 "NO_GPU_" + 哈希值
    
    Returns:
        str: 32位十六进制字符串的 GPU ID
    """
    gpu_info = None
    
    # 策略1: 使用 lspci -v 获取 GPU 信息
    try:
        result = subprocess.run(
            ['lspci', '-v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lspci_output = result.stdout
            
            # 查找 VGA compatible controller
            vga_pattern = r'(\S+)\s+VGA compatible controller:\s+(.+)'
            matches = re.findall(vga_pattern, lspci_output, re.MULTILINE)
            
            if matches:
                # 提取设备地址和设备名称
                gpu_devices = []
                for device_addr, device_name in matches:
                    # 清理设备名称
                    device_name = device_name.strip()
                    # 尝试提取设备ID (格式如: [10de:1f02])
                    device_id_pattern = r'\[([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\]'
                    device_id_match = re.search(device_id_pattern, device_name)
                    
                    if device_id_match:
                        device_id = device_id_match.group(1)
                        gpu_devices.append(f"{device_addr}:{device_id}")
                    else:
                        gpu_devices.append(f"{device_addr}:{device_name}")
                
                if gpu_devices:
                    gpu_info = "|".join(gpu_devices)
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    # 策略2: 备用方案 - 使用 nvidia-smi -L (NVIDIA GPU)
    if gpu_info is None:
        try:
            result = subprocess.run(
                ['nvidia-smi', '-L'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                nvidia_output = result.stdout
                
                # 解析 nvidia-smi 输出
                # 格式: GPU 0: NVIDIA GeForce RTX 3080 (UUID: GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
                gpu_pattern = r'GPU\s+\d+:\s+(.+?)\s+\(UUID:\s+([^)]+)\)'
                matches = re.findall(gpu_pattern, nvidia_output)
                
                if matches:
                    gpu_devices = []
                    for gpu_name, gpu_uuid in matches:
                        gpu_devices.append(f"{gpu_name.strip()}:{gpu_uuid.strip()}")
                    gpu_info = "|".join(gpu_devices)
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
    
    # 策略3: 如果都没有获取到，生成一个基于系统信息的哈希
    if gpu_info is None:
        # 使用系统信息生成一个稳定的"无GPU"标识
        system_info = f"{platform.machine()}:{platform.node()}:NO_GPU"
        hash_value = hashlib.md5(system_info.encode()).hexdigest()[:24]
        gpu_info = f"NO_GPU_{hash_value}"
    
    # 将 GPU 信息转换为 32 位十六进制字符串
    gpu_hash = hashlib.md5(gpu_info.encode()).hexdigest()
    
    # 确保返回 32 位 (MD5 默认就是 32 位十六进制)
    return gpu_hash[:32]


def get_linux_gpu_details() -> dict:
    """
    获取详细的 GPU 信息
    
    Returns:
        dict: 包含 GPU 详细信息的字典
    """
    details = {
        "gpu_id": get_linux_gpu_id(),
        "devices": [],
        "method": None,
        "raw_info": None
    }
    
    # 尝试 lspci
    try:
        result = subprocess.run(
            ['lspci', '-v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lspci_output = result.stdout
            vga_pattern = r'(\S+)\s+VGA compatible controller:\s+(.+)'
            matches = re.findall(vga_pattern, lspci_output, re.MULTILINE)
            
            if matches:
                details["method"] = "lspci"
                for device_addr, device_name in matches:
                    details["devices"].append({
                        "address": device_addr,
                        "name": device_name.strip()
                    })
                details["raw_info"] = gpu_info_to_raw(lspci_output)
                return details
    except Exception:
        pass
    
    # 尝试 nvidia-smi
    try:
        result = subprocess.run(
            ['nvidia-smi', '-L'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            nvidia_output = result.stdout
            gpu_pattern = r'GPU\s+\d+:\s+(.+?)\s+\(UUID:\s+([^)]+)\)'
            matches = re.findall(gpu_pattern, nvidia_output)
            
            if matches:
                details["method"] = "nvidia-smi"
                for gpu_name, gpu_uuid in matches:
                    details["devices"].append({
                        "name": gpu_name.strip(),
                        "uuid": gpu_uuid.strip()
                    })
                details["raw_info"] = nvidia_output
                return details
    except Exception:
        pass
    
    # 无 GPU
    details["method"] = "none"
    details["raw_info"] = "NO_GPU"
    
    return details


def gpu_info_to_raw(lspci_output: str) -> str:
    """
    从 lspci 输出中提取 GPU 相关的原始信息
    
    Args:
        lspci_output: lspci -v 的输出
        
    Returns:
        str: GPU 相关的原始信息
    """
    lines = lspci_output.split('\n')
    gpu_sections = []
    current_section = []
    in_gpu_section = False
    
    for line in lines:
        if 'VGA compatible controller' in line:
            if current_section:
                gpu_sections.append('\n'.join(current_section))
            current_section = [line]
            in_gpu_section = True
        elif in_gpu_section:
            # 检查是否是新设备的开头 (以地址格式如 00:00.0 开头)
            if re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f]', line):
                gpu_sections.append('\n'.join(current_section))
                current_section = []
                in_gpu_section = False
            else:
                current_section.append(line)
    
    if current_section:
        gpu_sections.append('\n'.join(current_section))
    
    return '\n\n'.join(gpu_sections) if gpu_sections else ""


if __name__ == "__main__":
    # 测试代码
    print("Linux GPU ID:", get_linux_gpu_id())
    print("\nDetailed Info:")
    details = get_linux_gpu_details()
    print(f"  Method: {details['method']}")
    print(f"  Devices: {details['devices']}")
