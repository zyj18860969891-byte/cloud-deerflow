#!/usr/bin/env python3
"""
修复 DEPLOYMENT_GUIDE.md 的 lint 错误
"""

import re

def fix_markdown_lint(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修复代码块语言标识
    # 为没有语言的代码块添加语言
    content = re.sub(r'```\n(.*?)\n```', r'```text\n\1\n```', content, flags=re.DOTALL)
    
    # 2. 修复代码块前后的空行
    # 确保代码块前后至少有一个空行
    content = re.sub(r'([^\n])\n```', r'\1\n\n```', content)
    content = re.sub(r'```\n([^\n])', r'```\n\n\1', content)
    
    # 3. 修复列表前后的空行
    # 确保列表前后有空行
    content = re.sub(r'([^\n])\n(- |\d+\. )', r'\1\n\n\2', content)
    content = re.sub(r'(- |\d+\. .*?)\n([^\n- \d])', r'\1\n\n\2', content)
    
    # 4. 修复裸URL
    # 将裸URL转换为链接
    content = re.sub(r'https?://[^\s<>\"\'`]+', r'<\g<0>>', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Markdown lint 修复完成")

if __name__ == '__main__':
    fix_markdown_lint('DEPLOYMENT_GUIDE.md')