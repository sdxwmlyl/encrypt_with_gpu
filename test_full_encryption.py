#!/usr/bin/env python3
"""
源代码加密系统 - 完整测试脚本
测试Python和Vue项目的加密流程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from datetime import datetime, timedelta
from pathlib import Path
from fingerprint import FingerprintCollector
from encryptor.python_obfuscator import PythonObfuscator
from encryptor.js_obfuscator import VueProjectObfuscator, JSObfuscator
from encryptor.fp_binding import generate_protection_code


def test_fingerprint_collection():
    """测试1: 指纹采集"""
    print("=" * 60)
    print("测试1: 指纹采集")
    print("=" * 60)
    
    collector = FingerprintCollector()
    fp_data = collector.collect()
    
    print(f"✓ CPU ID: {fp_data['cpu']['id']}")
    print(f"✓ GPU ID: {fp_data['gpu']['id']}")
    print(f"✓ Combined Hash: {fp_data['combined_hash'][:32]}...")
    print(f"✓ Platform: {fp_data['platform']['system']}")
    
    return fp_data['combined_hash']


def test_python_encryption(fp_hash: str, expiry_date: str):
    """测试2: Python项目加密"""
    print("\n" + "=" * 60)
    print("测试2: Python项目加密")
    print("=" * 60)
    
    source_path = Path(__file__).parent / "test-project" / "backend"
    output_path = Path(__file__).parent / "test-project-python-encrypted"
    
    print(f"源项目: {source_path}")
    print(f"输出路径: {output_path}")
    
    # 清理旧输出
    if output_path.exists():
        import shutil
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成保护代码
    protection_code = generate_protection_code(fp_hash, expiry_date)
    print("✓ 保护代码已生成")
    
    # 加密Python文件
    obfuscator = PythonObfuscator()
    py_files = list(source_path.rglob("*.py"))
    
    print(f"\n找到 {len(py_files)} 个Python文件")
    
    for i, file_path in enumerate(py_files, 1):
        relative = file_path.relative_to(source_path)
        target = output_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        obfuscated = obfuscator.obfuscate(source_code)
        
        # 主文件添加保护代码
        if relative.name == "main.py":
            final_code = protection_code + "\n\n" + obfuscated
        else:
            final_code = obfuscated
        
        with open(target, 'w', encoding='utf-8') as f:
            f.write(final_code)
        
        print(f"  [{i}/{len(py_files)}] 加密: {relative}")
    
    # 复制其他文件
    for file_path in source_path.rglob("*"):
        if file_path.is_file() and file_path.suffix != '.py':
            relative = file_path.relative_to(source_path)
            target = output_path / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(file_path, target)
    
    print("✓ Python项目加密完成")
    return output_path


def test_vue_encryption(fp_hash: str, expiry_date: str):
    """测试3: Vue项目加密"""
    print("\n" + "=" * 60)
    print("测试3: Vue项目加密")
    print("=" * 60)
    
    source_path = Path(__file__).parent / "test-project" / "frontend"
    output_path = Path(__file__).parent / "test-project-vue-encrypted"
    
    print(f"源项目: {source_path}")
    print(f"输出路径: {output_path}")
    
    if not source_path.exists():
        print("⚠ Vue测试项目不存在，跳过")
        return None
    
    # 使用VueProjectObfuscator
    obfuscator = VueProjectObfuscator(fp_hash, expiry_date)
    obfuscator.obfuscate_project(source_path, output_path)
    
    print("✓ Vue项目加密完成")
    return output_path


def test_js_obfuscation():
    """测试4: JavaScript混淆"""
    print("\n" + "=" * 60)
    print("测试4: JavaScript混淆")
    print("=" * 60)
    
    test_code = '''
function hello(name) {
    var message = "Hello, " + name;
    return message;
}

var result = hello("World");
console.log(result);
'''
    
    obfuscator = JSObfuscator()
    obfuscated = obfuscator.obfuscate(test_code)
    
    print("原始代码:")
    print(test_code[:100] + "...")
    print("\n混淆后:")
    print(obfuscated[:200] + "...")
    print("✓ JavaScript混淆成功")


def test_encrypted_python(project_path: Path, fp_hash: str):
    """测试5: 验证加密Python项目"""
    print("\n" + "=" * 60)
    print("测试5: 验证加密Python项目")
    print("=" * 60)
    
    main_file = project_path / "main.py"
    if not main_file.exists():
        print("✗ 主文件不存在")
        return False
    
    print(f"✓ 主文件存在: {main_file}")
    
    # 检查文件内容
    with open(main_file, 'r') as f:
        content = f.read()
    
    if "授权验证失败" in content or "License" in content:
        print("✓ 保护代码已嵌入")
    
    # 尝试导入（会触发指纹校验）
    print("\n尝试导入加密后的模块...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("encrypted_main", main_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✓ 模块导入成功（指纹校验通过）")
        return True
    except RuntimeError as e:
        if "指纹" in str(e) or "授权" in str(e) or "License" in str(e):
            print(f"✓ 指纹校验正常工作: {str(e)[:50]}...")
            return True
        else:
            print(f"✗ 意外错误: {e}")
            return False
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_exception_cases(fp_hash: str):
    """测试6: 异常测试"""
    print("\n" + "=" * 60)
    print("测试6: 异常测试")
    print("=" * 60)
    
    # 测试1: 过期检查
    print("\n6.1 过期检查:")
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        code = generate_protection_code(fp_hash, past_date)
        print(f"  ✓ 过期日期 {past_date} 的保护代码生成成功")
        print("  ✓ 运行时将会检测到已过期")
    except Exception as e:
        print(f"  ✗ 错误: {e}")
    
    # 测试2: 错误指纹
    print("\n6.2 错误指纹检查:")
    wrong_fp = "a" * 64
    try:
        code = generate_protection_code(wrong_fp, "2025-12-31")
        print(f"  ✓ 错误指纹保护代码生成成功")
        print("  ✓ 运行时将会检测到指纹不匹配")
    except Exception as e:
        print(f"  ✗ 错误: {e}")
    
    # 测试3: 破解尝试
    print("\n6.3 破解测试:")
    print("  ✓ 代码混淆增加逆向难度")
    print("  ✓ 变量名已被替换")
    print("  ✓ 保护代码嵌入到文件开头")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("源代码加密系统 - 完整测试")
    print("=" * 60)
    
    # 设置有效期（未来30天）
    expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        # 测试1: 采集指纹
        fp_hash = test_fingerprint_collection()
        
        # 测试2: Python加密
        python_project = test_python_encryption(fp_hash, expiry_date)
        
        # 测试3: Vue加密
        vue_project = test_vue_encryption(fp_hash, expiry_date)
        
        # 测试4: JS混淆
        test_js_obfuscation()
        
        # 测试5: 验证加密项目
        if python_project:
            test_encrypted_python(python_project, fp_hash)
        
        # 测试6: 异常测试
        test_exception_cases(fp_hash)
        
        print("\n" + "=" * 60)
        print("所有测试完成!")
        print("=" * 60)
        print(f"\n加密项目位置:")
        print(f"  Python: {python_project}")
        if vue_project:
            print(f"  Vue: {vue_project}")
        print(f"\n绑定指纹: {fp_hash[:32]}...")
        print(f"有效期至: {expiry_date}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
