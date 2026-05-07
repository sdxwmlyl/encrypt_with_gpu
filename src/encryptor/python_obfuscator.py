#!/usr/bin/env python3
"""
Python 代码混淆加密引擎
使用 AST 解析和混淆变量名、函数名
"""

import ast
import hashlib
import random
import string
import re
from typing import Set, Optional


class PythonObfuscator:
    """
    Python 代码混淆器
    使用简单的变量名替换进行混淆
    """
    
    def __init__(self):
        self.name_map = {}
        self.counter = 0
        # 保留的关键字和内置函数
        self.reserved = {
            'True', 'False', 'None', 'and', 'as', 'assert', 'break', 'class',
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'print', 'len', 'range', 'list',
            'dict', 'str', 'int', 'float', 'bool', 'tuple', 'set',
            'Exception', 'RuntimeError', 'ValueError', 'TypeError',
            '__name__', '__main__', '__file__', '__doc__', '__package__',
        }
    
    def _generate_name(self, original: str) -> str:
        """生成混淆后的名称"""
        if original in self.reserved or original.startswith('_'):
            return original
        if original not in self.name_map:
            # 生成形如 _0xABC123 的名称
            suffix = ''.join(random.choices(string.hexdigits.lower(), k=6))
            self.name_map[original] = f"_0x{suffix}"
        return self.name_map[original]
    
    def obfuscate(self, source_code: str) -> str:
        """
        混淆Python源代码
        
        Args:
            source_code: 原始Python代码
            
        Returns:
            混淆后的代码
        """
        try:
            # 解析AST
            tree = ast.parse(source_code)
            
            # 混淆名称
            self._obfuscate_names(tree)
            
            # 转换回代码
            # 使用ast.unparse (Python 3.9+) 或回退到原始代码
            if hasattr(ast, 'unparse'):
                return ast.unparse(tree)
            else:
                # 如果不支持unparse，返回原始代码
                return source_code
        except SyntaxError:
            # 如果解析失败，返回原始代码
            return source_code
    
    def _obfuscate_names(self, tree: ast.AST):
        """混淆AST中的名称"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    node.id = self._generate_name(node.id)
            elif isinstance(node, ast.FunctionDef):
                node.name = self._generate_name(node.name)
                # 混淆参数
                for arg in node.args.args:
                    arg.arg = self._generate_name(arg.arg)
            elif isinstance(node, ast.arg):
                node.arg = self._generate_name(node.arg)
    
    def obfuscate_simple(self, source_code: str) -> str:
        """
        简单的混淆方法：使用正则表达式替换变量名
        作为AST方法的备用方案
        """
        # 找到所有可能的标识符
        identifiers = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', source_code))
        
        # 过滤掉保留字
        to_obfuscate = identifiers - self.reserved
        
        # 创建映射
        name_map = {}
        counter = 0
        for name in to_obfuscate:
            if not name.startswith('_') and len(name) > 2:
                counter += 1
                suffix = ''.join(random.choices(string.hexdigits.lower(), k=6))
                name_map[name] = f"_0x{suffix}"
        
        # 替换
        result = source_code
        for old_name, new_name in name_map.items():
            # 使用正则确保只替换完整的标识符
            result = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, result)
        
        return result


if __name__ == "__main__":
    # 测试
    test_code = '''
def hello(name):
    message = "Hello, " + name
    return message

result = hello("World")
print(result)
'''
    
    obfuscator = PythonObfuscator()
    obfuscated = obfuscator.obfuscate_simple(test_code)
    print("原始代码:")
    print(test_code)
    print("\n混淆后:")
    print(obfuscated)
