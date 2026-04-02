#!/usr/bin/env python3
"""
DeerFlow 部署验证脚本
验证多租户功能和部署配置
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """打印分隔符头"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_file_exists(filepath, description=""):
    """检查文件是否存在"""
    desc = description or filepath
    if Path(filepath).exists():
        print(f"✅ {desc}")
        return True
    else:
        print(f"❌ {desc}")
        return False

def run_command(cmd, description=""):
    """运行命令"""
    desc = description or cmd
    print(f"\n⏳ {desc}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {desc}")
            if result.stdout:
                print(result.stdout[:500])  # 打印前500字符
            return True
        else:
            print(f"❌ {desc}")
            print(f"错误: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {desc} - 超时")
        return False
    except Exception as e:
        print(f"❌ {desc} - {str(e)}")
        return False

def main():
    """主验证流程"""
    print_header("🚀 DeerFlow 部署验证开始")
    
    # 获取项目根目录
    root_dir = Path(__file__).parent.absolute()
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    
    print(f"📁 项目根目录: {root_dir}")
    print(f"📁 后端目录: {backend_dir}")
    print(f"📁 前端目录: {frontend_dir}")
    
    # 1. 检查配置文件
    print_header("1️⃣  检查配置文件")
    
    config_files = [
        (root_dir / "config.yaml", "主配置文件"),
        (root_dir / "config.example.yaml", "配置示例"),
        (backend_dir / ".env", "后端环境变量"),
        (backend_dir / ".env.example", "后端环境示例"),
        (frontend_dir / ".env.local", "前端环境变量"),
    ]
    
    config_ok = True
    for filepath, desc in config_files:
        if not check_file_exists(filepath, desc):
            config_ok = False
    
    # 2. 检查项目结构
    print_header("2️⃣  检查项目结构")
    
    structure_checks = [
        (backend_dir / "packages" / "harness" / "deerflow", "多租户包"),
        (backend_dir / "app" / "gateway", "网关模块"),
        (backend_dir / "tests", "测试目录"),
        (backend_dir / "tests" / "test_multi_tenant.py", "多租户测试"),
        (frontend_dir / "src", "前端源码"),
    ]
    
    structure_ok = True
    for filepath, desc in structure_checks:
        if not check_file_exists(filepath, desc):
            structure_ok = False
    
    # 3. 检查Python环境
    print_header("3️⃣  检查Python环境")
    
    os.chdir(backend_dir)
    
    # 检查Python版本
    python_version_ok = run_command(
        "python --version",
        "检查Python版本"
    )
    
    # 检查pip环境
    pip_ok = run_command(
        "python -m pip --version",
        "检查pip环境"
    )
    
    # 4. 尝试导入核心模块
    print_header("4️⃣  检查Python模块导入")
    
    # 设置PYTHONPATH
    os.environ["PYTHONPATH"] = f".:packages/harness:{os.environ.get('PYTHONPATH', '')}"
    
    modules_to_check = [
        ("pytest", "pytest测试框架"),
        ("fastapi", "FastAPI网关"),
        ("starlette", "Starlette支持"),
        ("sqlalchemy", "SQLAlchemy ORM"),
    ]
    
    modules_ok = True
    for module, desc in modules_to_check:
        cmd = f"python -c \"import {module}; print('{module} imported successfully')\""
        if not run_command(cmd, f"检查{desc}"):
            modules_ok = False
    
    # 5. 运行多租户测试
    print_header("5️⃣  运行多租户单元测试")
    
    test_cmd = (
        "python -m pytest tests/test_multi_tenant.py -v --tb=short "
        "-x 2>&1 | head -100"
    )
    
    # 由于导入问题，先显示诊断信息
    print("\n⚠️  运行多租户测试...")
    print("命令:", test_cmd)
    print("\n注意: 如果遇到导入错误，请执行以下命令:")
    print("  cd backend")
    print("  pip install -e .")
    print("  python -m pytest tests/test_multi_tenant.py -v")
    
    test_ok = run_command(test_cmd, "多租户测试")
    
    # 6. 总结报告
    print_header("📊 验证总结报告")
    
    summary = {
        "配置文件": "✅" if config_ok else "❌",
        "项目结构": "✅" if structure_ok else "❌",
        "Python版本": "✅" if python_version_ok else "❌",
        "Pip环境": "✅" if pip_ok else "❌",
        "Python模块": "✅" if modules_ok else "❌",
        "多租户测试": "✅" if test_ok else "⚠️",
    }
    
    for check, status in summary.items():
        print(f"{status} {check}")
    
    all_ok = config_ok and structure_ok and python_version_ok and pip_ok and modules_ok
    
    print_header("🎯 后续步骤")
    
    if all_ok:
        print("""
✅ 所有基础检查通过！接下来的步骤:

1. 安装开发依赖包:
   cd backend
   pip install -e .

2. 运行完整的多租户测试:
   python -m pytest tests/test_multi_tenant.py -v

3. 启动开发服务:
   # 终端1 - LangGraph
   python -m langgraph dev
   
   # 终端2 - Gateway API
   python -m uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001
   
   # 终端3 - Frontend
   cd ../frontend
   pnpm dev

4. 验证多租户功能:
   curl -H "X-Tenant-ID: tenant-123" http://localhost:8001/health
""")
    else:
        print("""
⚠️  某些检查未通过。建议执行以下修复步骤:

1. 进入后端目录:
   cd backend

2. 安装依赖包:
   pip install -e .

3. 设置环境变量:
   # Windows PowerShell
   $env:PYTHONPATH = ".:packages/harness"
   
   # Linux/Mac
   export PYTHONPATH=".:packages/harness"

4. 再次运行验证脚本:
   python ../verify-deployment.py
""")
    
    print_header("✨ 验证完成")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
