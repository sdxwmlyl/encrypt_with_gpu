"""
Linux CPU ID 采集模块
从 /proc/cpuinfo 读取CPU信息并生成唯一标识符
"""

import hashlib
import re
from typing import Optional


def get_linux_cpu_id() -> str:
    """
    获取Linux系统的CPU唯一标识符
    
    1. 尝试从 /proc/cpuinfo 提取 serial 字段
    2. 如果 serial 不存在，使用 processor + model name 组合哈希
    3. 返回32位十六进制字符串
    
    Returns:
        str: 32位十六进制CPU标识符
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
    except (IOError, OSError) as e:
        raise RuntimeError(f"无法读取 /proc/cpuinfo: {e}")
    
    # 尝试提取 serial 字段
    serial = _extract_serial(cpuinfo)
    if serial:
        return _hash_to_32hex(serial)
    
    # serial 不存在，使用 processor + model name 组合
    processor_info = _extract_processor_info(cpuinfo)
    if not processor_info:
        raise RuntimeError("无法从 /proc/cpuinfo 提取CPU信息")
    
    combined = f"{processor_info['processor']}|{processor_info['model_name']}"
    return _hash_to_32hex(combined)


def _extract_serial(cpuinfo: str) -> Optional[str]:
    """
    从 cpuinfo 内容中提取 serial 字段
    
    Args:
        cpuinfo: /proc/cpuinfo 的完整内容
        
    Returns:
        Optional[str]: serial 值，如果不存在则返回 None
    """
    # 查找 Serial 或 serial 字段（常见于ARM架构）
    patterns = [
        r'(?im)^Serial\s*:\s*(.+)$',
        r'(?im)^serial\s*:\s*(.+)$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cpuinfo)
        if match:
            return match.group(1).strip()
    
    return None


def _extract_processor_info(cpuinfo: str) -> Optional[dict]:
    """
    从 cpuinfo 内容中提取 processor 和 model name
    
    Args:
        cpuinfo: /proc/cpuinfo 的完整内容
        
    Returns:
        Optional[dict]: 包含 processor 和 model_name 的字典
    """
    # 提取第一个CPU核心的信息
    # 按空行分割，获取第一个CPU块
    cpu_blocks = cpuinfo.strip().split('\n\n')
    if not cpu_blocks:
        return None
    
    first_block = cpu_blocks[0]
    
    processor = None
    model_name = None
    
    # 提取 processor 字段
    proc_match = re.search(r'(?im)^processor\s*:\s*(.+)$', first_block)
    if proc_match:
        processor = proc_match.group(1).strip()
    
    # 提取 model name 字段（可能有不同写法）
    model_patterns = [
        r'(?im)^model name\s*:\s*(.+)$',
        r'(?im)^model_name\s*:\s*(.+)$',
        r'(?im)^cpu model\s*:\s*(.+)$',
    ]
    
    for pattern in model_patterns:
        model_match = re.search(pattern, first_block)
        if model_match:
            model_name = model_match.group(1).strip()
            break
    
    # 如果没有 model name，尝试使用 model 和 cpu family
    if not model_name:
        model_num = None
        family_num = None
        
        model_match = re.search(r'(?im)^model\s*:\s*(\d+)$', first_block)
        if model_match:
            model_num = model_match.group(1).strip()
        
        family_match = re.search(r'(?im)^cpu family\s*:\s*(\d+)$', first_block)
        if family_match:
            family_num = family_match.group(1).strip()
        
        if model_num and family_num:
            model_name = f"Family{family_num}_Model{model_num}"
    
    if processor and model_name:
        return {
            'processor': processor,
            'model_name': model_name
        }
    
    return None


def _hash_to_32hex(data: str) -> str:
    """
    将字符串哈希为32位十六进制字符串
    
    Args:
        data: 输入字符串
        
    Returns:
        str: 32位十六进制字符串
    """
    # 使用 SHA-256 哈希，然后取前32位
    hash_bytes = hashlib.sha256(data.encode('utf-8')).digest()
    # 转换为十六进制，取前32个字符
    return hash_bytes.hex()[:32]


# 向后兼容的别名
get_cpu_id = get_linux_cpu_id


if __name__ == '__main__':
    # 测试代码
    try:
        cpu_id = get_linux_cpu_id()
        print(f"Linux CPU ID: {cpu_id}")
        print(f"Length: {len(cpu_id)} characters")
    except Exception as e:
        print(f"Error: {e}")
