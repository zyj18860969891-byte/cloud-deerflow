#!/usr/bin/env python3
"""
批量替换 datetime.utcnow() -> datetime.now(datetime.UTC)

这个脚本扫描所有 Python 文件，将弃用的 utcnow() 调用替换为新的 now(datetime.UTC) 方式。
"""

import re
from pathlib import Path


def replace_utcnow_in_file(file_path: str) -> tuple[int, int]:
    """
    在单个文件中替换 utcnow() 调用。
    返回 (替换数, 文件大小)
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # 替换所有 datetime.utcnow() 调用
    # 注意：需要处理各种情况，如带参数的、链式调用等

    # 简单的直接替换
    content = re.sub(r"datetime\.utcnow\(\)", "datetime.now(datetime.UTC)", content)

    # 计算替换数
    replacements = len(re.findall(r"datetime\.now\(datetime\.UTC\)", content)) - len(re.findall(r"datetime\.now\(datetime\.UTC\)", original_content))

    # 检查是否需要添加 datetime.UTC 到导入
    if "datetime.now(datetime.UTC)" in content and "datetime.UTC" not in original_content:
        # 检查是否有 from datetime import ... 语句
        if re.search(r"from datetime import", content):
            # 添加 UTC 到现有导入
            content = re.sub(r"(from datetime import [^\n]*)", lambda m: m.group(1) if "UTC" in m.group(1) else m.group(1).rstrip(")") + ", UTC)", content, flags=re.MULTILINE)
        else:
            # 在 datetime 导入行之后添加 UTC 导入
            content = re.sub(r"(from datetime import datetime(?:, timedelta)?)", r"\1, UTC", content)

    if replacements > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return replacements, len(original_content)


def main():
    backend_dir = Path("/d/MultiMode/deerflow/deer-flow/backend")

    if not backend_dir.exists():
        print(f"❌ 后端目录不存在: {backend_dir}")
        return

    total_replacements = 0
    modified_files = []

    # 查找所有 Python 文件
    for py_file in backend_dir.rglob("*.py"):
        # 跳过虚拟环境和缓存目录
        if any(part in py_file.parts for part in ["venv", "__pycache__", ".pytest_cache", "node_modules"]):
            continue

        try:
            replacements, size = replace_utcnow_in_file(str(py_file))
            if replacements > 0:
                relative_path = py_file.relative_to(backend_dir)
                modified_files.append((str(relative_path), replacements))
                total_replacements += replacements
                print(f"✅ {relative_path}: {replacements} 处替换")
        except Exception as e:
            print(f"⚠️ {py_file}: {str(e)}")

    print(f"\n{'=' * 50}")
    print(f"总计: {total_replacements} 处替换，{len(modified_files)} 个文件修改")
    print(f"{'=' * 50}")

    if modified_files:
        print("\n修改的文件列表:")
        for file_path, count in modified_files:
            print(f"  • {file_path} ({count} 处)")


if __name__ == "__main__":
    main()
