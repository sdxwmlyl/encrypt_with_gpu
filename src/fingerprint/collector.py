"""
指纹统一采集模块
自动检测操作系统并采集CPU/GPU指纹信息
"""

import hashlib
import platform
from typing import Dict, Optional, Any


class FingerprintCollector:
    """
    指纹采集器类
    
    自动检测操作系统(Linux/Windows)，提供统一的指纹采集接口。
    支持采集CPU和GPU的硬件指纹信息。
    
    Attributes:
        os_type: 检测到的操作系统类型 ('linux' 或 'windows')
        _cpu_id: 缓存的CPU ID
        _gpu_id: 缓存的GPU ID
    """
    
    def __init__(self):
        """初始化指纹采集器，自动检测操作系统类型。"""
        self.os_type = self._detect_os()
        self._cpu_id: Optional[str] = None
        self._gpu_id: Optional[str] = None
        self._cpu_module = None
        self._gpu_module = None
        self._load_modules()
    
    def _detect_os(self) -> str:
        """
        检测当前操作系统类型。
        
        Returns:
            str: 'linux' 或 'windows'
            
        Raises:
            RuntimeError: 如果操作系统不受支持
        """
        system = platform.system().lower()
        if system == 'linux':
            return 'linux'
        elif system == 'windows':
            return 'windows'
        else:
            raise RuntimeError(f"不支持的操作系统: {platform.system()}")
    
    def _load_modules(self):
        """动态加载对应平台的CPU/GPU采集模块。"""
        if self.os_type == 'linux':
            from . import cpu_linux, gpu_linux
            self._cpu_module = cpu_linux
            self._gpu_module = gpu_linux
        else:  # windows
            from . import cpu_windows, gpu_windows
            self._cpu_module = cpu_windows
            self._gpu_module = gpu_windows
    
    def collect(self) -> Dict[str, Any]:
        """
        采集完整的指纹信息。
        
        采集当前系统的CPU和GPU指纹，并返回格式化的字典。
        
        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - os_type: 操作系统类型 ('linux' 或 'windows')
                - platform: 平台详细信息
                - cpu: CPU指纹信息字典
                - gpu: GPU指纹信息字典
                - combined_hash: 组合哈希值 (CPU+GPU)
                - timestamp: 采集时间戳
        
        Example:
            >>> collector = FingerprintCollector()
            >>> fp = collector.collect()
            >>> print(fp['combined_hash'])
            'a1b2c3d4...'
        """
        import time
        
        cpu_id = self.get_cpu_id()
        gpu_id = self.get_gpu_id()
        combined = self.get_combined_hash()
        
        return {
            'os_type': self.os_type,
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'node': platform.node()
            },
            'cpu': {
                'id': cpu_id,
                'source': 'cpu_linux' if self.os_type == 'linux' else 'cpu_windows'
            },
            'gpu': {
                'id': gpu_id,
                'source': 'gpu_linux' if self.os_type == 'linux' else 'gpu_windows'
            },
            'combined_hash': combined,
            'timestamp': int(time.time())
        }
    
    def get_cpu_id(self) -> str:
        """
        获取CPU指纹ID。
        
        根据检测到的操作系统，调用对应的CPU采集模块。
        结果会被缓存以提高性能。
        
        Returns:
            str: 32位十六进制CPU指纹字符串
            
        Raises:
            RuntimeError: 如果CPU信息采集失败
        """
        if self._cpu_id is None:
            if self.os_type == 'linux':
                self._cpu_id = self._cpu_module.get_linux_cpu_id()
            else:
                self._cpu_id = self._cpu_module.get_windows_cpu_id()
        return self._cpu_id
    
    def get_gpu_id(self) -> str:
        """
        获取GPU指纹ID。
        
        根据检测到的操作系统，调用对应的GPU采集模块。
        结果会被缓存以提高性能。
        
        Returns:
            str: 32位十六进制GPU指纹字符串
            
        Note:
            如果GPU信息采集失败，会返回一个基于系统信息的替代值
        """
        if self._gpu_id is None:
            if self.os_type == 'linux':
                self._gpu_id = self._gpu_module.get_linux_gpu_id()
            else:
                gpu_result = self._gpu_module.get_windows_gpu_id()
                # Windows GPU模块可能返回None
                if gpu_result is None:
                    # 生成一个基于系统信息的替代值
                    fallback = f"NO_GPU_{platform.node()}_{platform.machine()}"
                    self._gpu_id = hashlib.md5(fallback.encode()).hexdigest()[:32]
                else:
                    self._gpu_id = gpu_result
        return self._gpu_id
    
    def get_combined_hash(self) -> str:
        """
        获取CPU和GPU的组合哈希。
        
        将CPU ID和GPU ID组合后进行SHA-256哈希，生成唯一的设备指纹。
        
        Returns:
            str: 64位十六进制组合哈希字符串
            
        Example:
            >>> collector = FingerprintCollector()
            >>> hash_val = collector.get_combined_hash()
            >>> len(hash_val)
            64
        """
        cpu_id = self.get_cpu_id()
        gpu_id = self.get_gpu_id()
        
        # 组合CPU和GPU ID
        combined = f"{cpu_id}:{gpu_id}"
        
        # 使用SHA-256生成64位十六进制哈希
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def refresh(self) -> 'FingerprintCollector':
        """
        刷新指纹缓存。
        
        清除已缓存的CPU和GPU ID，下次调用时会重新采集。
        
        Returns:
            FingerprintCollector: 返回自身，支持链式调用
            
        Example:
            >>> collector.refresh().collect()
        """
        self._cpu_id = None
        self._gpu_id = None
        return self
    
    def verify(self, expected_combined_hash: str) -> bool:
        """
        验证给定的组合哈希是否匹配当前设备。
        
        Args:
            expected_combined_hash: 预期的组合哈希值
            
        Returns:
            bool: 如果匹配返回True，否则返回False
            
        Example:
            >>> collector = FingerprintCollector()
            >>> collector.verify('expected_hash_here')
            True
        """
        current_hash = self.get_combined_hash()
        return current_hash == expected_combined_hash


# 便捷函数
def collect_fingerprint() -> Dict[str, Any]:
    """
    快速采集指纹信息的便捷函数。
    
    Returns:
        Dict[str, Any]: 完整的指纹信息字典
        
    Example:
        >>> from fingerprint.collector import collect_fingerprint
        >>> fp = collect_fingerprint()
        >>> print(fp['combined_hash'])
    """
    collector = FingerprintCollector()
    return collector.collect()


def get_device_hash() -> str:
    """
    快速获取设备组合哈希的便捷函数。
    
    Returns:
        str: 64位十六进制设备组合哈希
        
    Example:
        >>> from fingerprint.collector import get_device_hash
        >>> device_id = get_device_hash()
    """
    collector = FingerprintCollector()
    return collector.get_combined_hash()


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("指纹采集器测试")
    print("=" * 60)
    
    try:
        collector = FingerprintCollector()
        
        print(f"\n操作系统类型: {collector.os_type}")
        print(f"平台: {platform.system()} {platform.release()}")
        print(f"机器: {platform.machine()}")
        
        print("\n--- 单独采集 ---")
        cpu_id = collector.get_cpu_id()
        print(f"CPU ID: {cpu_id}")
        print(f"CPU ID长度: {len(cpu_id)}")
        
        gpu_id = collector.get_gpu_id()
        print(f"GPU ID: {gpu_id}")
        print(f"GPU ID长度: {len(gpu_id)}")
        
        combined = collector.get_combined_hash()
        print(f"\n组合哈希: {combined}")
        print(f"组合哈希长度: {len(combined)}")
        
        print("\n--- 完整采集 ---")
        full_fp = collector.collect()
        import json
        print(json.dumps(full_fp, indent=2))
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()