"""
指纹采集模块

提供统一的硬件指纹采集接口，支持Linux和Windows系统。
自动检测操作系统并调用对应的采集模块。

主要组件:
    - FingerprintCollector: 主采集器类
    - cpu_linux: Linux CPU采集模块
    - gpu_linux: Linux GPU采集模块
    - cpu_windows: Windows CPU采集模块
    - gpu_windows: Windows GPU采集模块

使用示例:
    >>> from fingerprint import FingerprintCollector
    >>> collector = FingerprintCollector()
    >>> fp = collector.collect()
    >>> print(fp['combined_hash'])
    
    >>> # 快速获取设备哈希
    >>> from fingerprint import get_device_hash
    >>> device_id = get_device_hash()
"""

from .collector import FingerprintCollector, collect_fingerprint, get_device_hash

__version__ = '1.0.0'
__author__ = 'Encryption System'

__all__ = [
    'FingerprintCollector',
    'collect_fingerprint',
    'get_device_hash',
]
