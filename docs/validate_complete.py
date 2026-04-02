#!/usr/bin/env python3
"""
最终验证 DEPLOYMENT_GUIDE.md 的完整性
"""

import markdown
from markdown.extensions.tables import TableExtension

def validate_document():
    with open('DEPLOYMENT_GUIDE.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    md = markdown.Markdown(extensions=['tables'])
    html = md.convert(content)
    
    print("=" * 60)
    print("DeerFlow 部署指南最终验证")
    print("=" * 60)
    
    # 检查关键章节
    sections = [
        ('版本信息', '版本信息'),
        ('架构特性', '0. DeerFlow 架构特性详解'),
        ('服务提供方快速部署指南', '十六、服务提供方快速部署指南'),
        ('管理控制台完整实现指南', '十七、管理控制台完整实现指南'),
        ('Railway快速部署原型', '十八、Railway快速部署管理控制台原型'),
        ('季度订阅机制', '十九、季度订阅机制实现'),
        ('版本历史', '版本历史'),
    ]
    
    print("\n1. 章节检查:")
    for name, title in sections:
        if title in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} 缺失")
    
    # 检查表格
    table_count = html.count('<table>')
    print(f"\n2. 表格检查: {table_count} 个表格")
    
    # 检查代码块
    code_blocks = content.count('```')
    print(f"\n3. 代码块检查: {code_blocks // 2} 个代码块")
    
    # 检查关键内容
    key_content = [
        ('管理控制台', '管理控制台'),
        ('数据库设计', '数据库架构设计'),
        ('API设计', 'REST API 设计'),
        ('前端组件', '前端组件设计'),
        ('部署引擎', 'DeploymentEngine'),
        ('Railway', 'Railway'),
        ('Docker Compose', 'Docker Compose'),
        ('Kubernetes', 'Kubernetes'),
        ('加密', 'ConfigEncryption'),
        ('监控', 'MonitorService'),
        ('Stripe', 'Stripe'),
        ('订阅', 'subscription'),
        ('Webhook', 'webhook')
    ]
    
    print("\n4. 关键内容检查:")
    for name, keyword in key_content:
        if keyword in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} 缺失")
    
    # 文档统计
    print("\n5. 文档统计:")
    print(f"   - Markdown 长度: {len(content):,} 字符")
    print(f"   - HTML 长度: {len(html):,} 字符")
    print(f"   - 总行数: {content.count(chr(10)):,} 行")
    print(f"   - 标题数量: {html.count('<h1>') + html.count('<h2>') + html.count('<h3>') + html.count('<h4>') + html.count('<h5>')}")
    
    print("\n" + "=" * 60)
    print("✅ 文档验证完成！")
    print("=" * 60)

if __name__ == '__main__':
    validate_document()