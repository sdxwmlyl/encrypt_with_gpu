#!/usr/bin/env python3
"""
JavaScript/Vue 代码混淆加密引擎
支持JS文件混淆和Vue单文件组件处理
"""

import re
import random
import string
import hashlib
import base64
import shutil
from pathlib import Path
from typing import Set, Dict, List


class JSObfuscator:
    """JavaScript 代码混淆器"""
    
    def __init__(self):
        self.name_map: Dict[str, str] = {}
        self.counter = 0
        self.reserved = {
            'break', 'case', 'catch', 'continue', 'debugger', 'default', 'delete',
            'do', 'else', 'finally', 'for', 'function', 'if', 'in', 'instanceof',
            'new', 'return', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
            'void', 'while', 'with', 'class', 'const', 'enum', 'export', 'extends',
            'import', 'super', 'implements', 'interface', 'let', 'package', 'private',
            'protected', 'public', 'static', 'yield', 'await', 'true', 'false', 'null',
            'undefined', 'NaN', 'Infinity', 'console', 'window', 'document', 'navigator',
            'location', 'localStorage', 'sessionStorage', 'fetch', 'axios', 'Vue',
            'ref', 'reactive', 'computed', 'watch', 'onMounted', 'onUnmounted',
            'createApp', 'defineComponent', 'defineProps', 'defineEmits', 'defineExpose',
            'useRoute', 'useRouter', 'nextTick', 'provide', 'inject', 'h'
        }
    
    def _generate_name(self, original: str) -> str:
        if original in self.reserved or original.startswith('_'):
            return original
        if original not in self.name_map:
            self.counter += 1
            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            self.name_map[original] = f"_{suffix}"
        return self.name_map[original]
    
    def obfuscate(self, code: str) -> str:
        code = self._remove_comments(code)
        code = self._obfuscate_identifiers(code)
        code = self._compress_whitespace(code)
        return code
    
    def _remove_comments(self, code: str) -> str:
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code
    
    def _obfuscate_identifiers(self, code: str) -> str:
        var_pattern = r'\b(var|let|const)\s+(\w+)'
        func_pattern = r'\bfunction\s+(\w+)'
        
        identifiers = set()
        for match in re.finditer(var_pattern, code):
            identifiers.add(match.group(2))
        for match in re.finditer(func_pattern, code):
            identifiers.add(match.group(1))
        
        to_obfuscate = identifiers - self.reserved
        name_map = {}
        for name in to_obfuscate:
            if len(name) > 2 and not name.startswith('_'):
                suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                name_map[name] = f"_{suffix}"
        
        result = code
        for old_name, new_name in name_map.items():
            result = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, result)
        return result
    
    def _compress_whitespace(self, code: str) -> str:
        code = re.sub(r'^\s+', '', code, flags=re.MULTILINE)
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'\s+$', '', code, flags=re.MULTILINE)
        return code
    
    def obfuscate_vue_file(self, content: str, fingerprint: str, expiry: str) -> str:
        template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
        script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
        
        result = []
        
        if template_match:
            template = template_match.group(1)
            template = self._compress_whitespace(template)
            result.append(f'<template>{template}</template>')
        
        if script_match:
            script = script_match.group(1)
            protection = self._generate_js_protection(fingerprint, expiry)
            obfuscated_script = self.obfuscate(script)
            result.append(f'<script>\n{protection}\n{obfuscated_script}\n</script>')
        
        if style_match:
            style = style_match.group(1)
            result.append(f'<style>{style}</style>')
        
        return '\n\n'.join(result)
    
    def _generate_js_protection(self, fingerprint: str, expiry: str) -> str:
        fp_b64 = base64.b64encode(fingerprint.encode()).decode()
        exp_b64 = base64.b64encode(expiry.encode()).decode()
        
        protection = f'''// License Protection
(function(){{
    var _fp="{fp_b64[:50]}...";
    var _ex="{exp_b64}";
    var _d=new Date();
    var _e=new Date(atob(_ex));
    if(_d>_e){{
        throw new Error("License expired: "+atob(_ex));
    }}
}})();'''
        return protection


class VueProjectObfuscator:
    """Vue项目混淆器"""
    
    def __init__(self, fingerprint: str, expiry: str):
        self.fingerprint = fingerprint
        self.expiry = expiry
        self.js_obfuscator = JSObfuscator()
    
    def obfuscate_project(self, source_path: Path, output_path: Path):
        if output_path.exists():
            shutil.rmtree(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for item in source_path.rglob('*'):
            if item.is_file():
                relative = item.relative_to(source_path)
                target = output_path / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                
                if item.suffix == '.vue':
                    with open(item, 'r', encoding='utf-8') as f:
                        content = f.read()
                    obfuscated = self.js_obfuscator.obfuscate_vue_file(
                        content, self.fingerprint, self.expiry
                    )
                    with open(target, 'w', encoding='utf-8') as f:
                        f.write(obfuscated)
                elif item.suffix in ['.js', '.ts']:
                    with open(item, 'r', encoding='utf-8') as f:
                        content = f.read()
                    obfuscated = self.js_obfuscator.obfuscate(content)
                    protection = self.js_obfuscator._generate_js_protection(
                        self.fingerprint, self.expiry
                    )
                    with open(target, 'w', encoding='utf-8') as f:
                        f.write(protection + '\n' + obfuscated)
                else:
                    shutil.copy2(item, target)


if __name__ == "__main__":
    # 测试
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
    print(test_code)
    print("\n混淆后:")
    print(obfuscated)
