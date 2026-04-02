#!/usr/bin/env python3
"""
DeerFlow 生产部署验证工具
检查部署前的所有必需配置和系统状态
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class DeploymentValidator:
    """DeerFlow 部署验证工具"""

    def __init__(self, repo_root: str = None, data_dir: str = None):
        self.repo_root = Path(repo_root or os.getenv('DEER_FLOW_REPO_ROOT', '/opt/deer-flow'))
        self.data_dir = Path(data_dir or os.getenv('DEER_FLOW_HOME', '/data/deer-flow/.deer-flow'))
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }

    def check_system_requirements(self) -> List[Dict[str, Any]]:
        """检查系统要求"""
        print("=" * 60)
        print("📋 系统环境检查")
        print("=" * 60)

        checks = [
            ("Python 3.12+", self._check_python),
            ("Node.js 22+", self._check_nodejs),
            ("Docker", self._check_docker),
            ("Docker Compose", self._check_docker_compose),
            ("pnpm", self._check_pnpm),
            ("uv", self._check_uv),
            ("git", self._check_git),
        ]

        results = []
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "pass" if result["status"] else "fail"
                symbol = "✅" if result["status"] else "❌"

                print(f"{symbol} {check_name}: {result['message']}")
                self._add_check_result(check_name, status, result.get("version"), result.get("error"))
                results.append({
                    "name": check_name,
                    "status": status,
                    "message": result["message"],
                    "version": result.get("version")
                })
            except Exception as e:
                print(f"❌ {check_name}: {str(e)}")
                self._add_check_result(check_name, "error", error=str(e))
                results.append({
                    "name": check_name,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def check_directories(self) -> List[Dict[str, Any]]:
        """检查数据目录"""
        print("\n" + "=" * 60)
        print("📂 数据目录检查")
        print("=" * 60)

        required_dirs = [
            self.data_dir,
            self.data_dir / "skills",
            self.data_dir / "logs",
            self.data_dir / "tenants",
            self.data_dir / "backup",
            self.repo_root / "config.yaml",
            self.repo_root / "docker",
            self.repo_root / "skills",
        ]

        results = []
        for dir_path in required_dirs:
            if isinstance(dir_path, Path) and not dir_path.is_file():
                exists = dir_path.exists()
                status = "pass" if exists else "fail"
                symbol = "✅" if exists else "❌"
                print(f"{symbol} Directory: {dir_path}")
                self._add_check_result(f"Directory: {dir_path.name}", status)
                results.append({
                    "path": str(dir_path),
                    "status": status,
                    "exists": exists
                })
            elif isinstance(dir_path, Path) and dir_path.is_file():
                exists = dir_path.exists()
                status = "pass" if exists else "fail"
                symbol = "✅" if exists else "❌"
                print(f"{symbol} File: {dir_path}")
                self._add_check_result(f"File: {dir_path.name}", status)
                results.append({
                    "path": str(dir_path),
                    "status": status,
                    "exists": exists
                })

        return results

    def check_config_files(self) -> List[Dict[str, Any]]:
        """检查配置文件"""
        print("\n" + "=" * 60)
        print("⚙️  配置文件检查")
        print("=" * 60)

        config_files = [
            ("config.yaml", self.repo_root / "config.yaml"),
            ("extensions_config.json", self.repo_root / "extensions_config.json"),
            ("docker-compose.yaml", self.repo_root / "docker" / "docker-compose.yaml"),
            ("nginx.conf", self.repo_root / "docker" / "nginx" / "nginx.conf"),
        ]

        results = []
        for config_name, config_file in config_files:
            exists = config_file.exists()
            status = "pass" if exists else "warning"
            symbol = "✅" if exists else "⚠️"

            print(f"{symbol} {config_name}: {config_file}")

            if exists:
                # 验证配置文件内容
                validation = self._validate_config_file(config_file, config_name)
                if validation["valid"]:
                    print(f"   ✓ 配置格式正确")
                else:
                    print(f"   ✗ 配置错误: {validation['error']}")
                    status = "fail"
                    symbol = "❌"

            self._add_check_result(f"Config: {config_name}", status)
            results.append({
                "name": config_name,
                "path": str(config_file),
                "status": status,
                "exists": exists
            })

        return results

    def check_environment_variables(self) -> List[Dict[str, Any]]:
        """检查必需的环境变量"""
        print("\n" + "=" * 60)
        print("🔐 环境变量检查")
        print("=" * 60)

        required_vars = [
            ("BETTER_AUTH_SECRET", "认证密钥", True),
            ("OPENAI_API_KEY", "OpenAI API密钥", True),
            ("DEER_FLOW_MULTI_TENANT_ENABLED", "多租户启用", False),
            ("DEER_FLOW_TENANT_ISOLATION_LEVEL", "租户隔离级别", False),
        ]

        optional_vars = [
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "DEEPSEEK_API_KEY",
            "FEISHU_APP_ID",
            "FEISHU_APP_SECRET",
            "SLACK_BOT_TOKEN",
            "TELEGRAM_BOT_TOKEN",
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",
            "REDIS_HOST",
            "REDIS_PORT",
        ]

        results = []

        # 检查必需变量
        for var_name, description, required in required_vars:
            value = os.getenv(var_name)
            if required and not value:
                status = "fail"
                symbol = "❌"
                print(f"{symbol} {var_name} ({description}): 未设置 (必需)")
                self._add_check_result(f"Env: {var_name}", status, error="Required variable not set")
            elif value:
                status = "pass"
                symbol = "✅"
                # 隐藏敏感信息
                display_value = value[:8] + "..." if len(value) > 8 else value
                print(f"{symbol} {var_name} ({description}): 已设置")
            else:
                status = "warning"
                symbol = "⚠️"
                print(f"{symbol} {var_name} ({description}): 未设置 (可选)")
                self._add_check_result(f"Env: {var_name}", status)

            results.append({
                "name": var_name,
                "description": description,
                "required": required,
                "status": status,
                "set": bool(value)
            })

        # 检查可选变量
        print("\n可选环境变量:")
        for var_name in optional_vars:
            value = os.getenv(var_name)
            status = "pass" if value else "warning"
            symbol = "✅" if value else "⭕"
            print(f"{symbol} {var_name}: {'已设置' if value else '未设置 (可选)'}")

        return results

    def check_docker_images(self) -> List[Dict[str, Any]]:
        """检查Docker镜像"""
        print("\n" + "=" * 60)
        print("🐳 Docker 镜像检查")
        print("=" * 60)

        required_images = [
            "nginx:alpine",
            "python:3.12-slim",
            "node:22-alpine",
            "postgres:16-alpine",
            "redis:7-alpine",
        ]

        results = []
        for image in required_images:
            try:
                result = subprocess.run(
                    ["docker", "image", "inspect", image],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                exists = result.returncode == 0
                status = "pass" if exists else "warning"
                symbol = "✅" if exists else "⚠️"

                print(f"{symbol} {image}: {'已存在' if exists else '需要拉取'}")
                self._add_check_result(f"Docker: {image}", status)

                results.append({
                    "image": image,
                    "status": status,
                    "exists": exists
                })
            except subprocess.TimeoutExpired:
                print(f"⏰ {image}: 检查超时")
                results.append({
                    "image": image,
                    "status": "error",
                    "error": "Timeout"
                })
            except Exception as e:
                print(f"❌ {image}: 检查失败 - {str(e)}")
                self._add_check_result(f"Docker: {image}", "error", error=str(e))
                results.append({
                    "image": image,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def check_network_ports(self) -> List[Dict[str, Any]]:
        """检查端口占用"""
        print("\n" + "=" * 60)
        print("🌐 端口占用检查")
        print("=" * 60)

        required_ports = [
            (2026, "Nginx反向代理"),
            (3000, "前端服务"),
            (8001, "Gateway API"),
            (2024, "LangGraph"),
            (5432, "PostgreSQL"),
            (6379, "Redis"),
        ]

        results = []
        for port, service in required_ports:
            try:
                # Windows PowerShell命令检查端口占用
                if sys.platform == "win32":
                    cmd = f"netstat -ano | findstr :{port}"
                else:
                    cmd = f"lsof -i :{port}"

                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                in_use = result.returncode == 0 and result.stdout.strip()
                status = "warning" if in_use else "pass"
                symbol = "⚠️" if in_use else "✅"

                if in_use:
                    print(f"{symbol} 端口 {port} ({service}): 已被占用")
                    # 提取PID（仅Unix系统）
                    if sys.platform != "win32":
                        lines = result.stdout.strip().split('\n')
                        if lines:
                            parts = lines[0].split()
                            if len(parts) > 6:
                                pid = parts[6]
                                print(f"   进程ID: {pid}")
                else:
                    print(f"{symbol} 端口 {port} ({service}): 可用")

                self._add_check_result(f"Port: {port}", status if in_use else "pass")
                results.append({
                    "port": port,
                    "service": service,
                    "status": status if in_use else "pass",
                    "in_use": bool(in_use)
                })
            except Exception as e:
                print(f"❌ 端口 {port} 检查失败: {str(e)}")
                results.append({
                    "port": port,
                    "service": service,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def generate_report(self) -> str:
        """生成检查报告"""
        print("\n" + "=" * 60)
        print("📊 部署验证报告")
        print("=" * 60)

        total = len(self.results["checks"])
        passed = sum(1 for c in self.results["checks"] if c["status"] == "pass")
        failed = sum(1 for c in self.results["checks"] if c["status"] == "fail")
        warnings = sum(1 for c in self.results["checks"] if c["status"] == "warning")
        errors = sum(1 for c in self.results["checks"] if c["status"] == "error")

        print(f"\n总计: {total} 项检查")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⚠️  警告: {warnings}")
        print(f"🚨 错误: {errors}")

        if failed == 0 and errors == 0:
            print("\n🎉 所有检查都通过了！")
            print("可以开始启动 DeerFlow 服务了。")
            print("\n下一步:")
            print("1. 确保 .env.production 文件已配置所有必需的API密钥")
            print("2. 运行: docker-compose -f docker/docker-compose.yaml up -d")
            print("3. 验证服务: curl http://localhost:2026/health")
        else:
            print("\n⚠️  请解决上述问题后再启动服务。")
            print("\n常见问题:")
            print("- 确保所有必需的环境变量已设置")
            print("- 检查端口是否被其他程序占用")
            print("- 确认Docker镜像已拉取")
            print("- 验证配置文件格式正确")

        # 保存JSON报告
        report_file = self.repo_root / "deployment_validation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细报告已保存到: {report_file}")

        return report_file

    def _add_check_result(self, name: str, status: str, value: Any = None, error: str = None):
        """添加检查结果"""
        check_result = {
            "name": name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if value is not None:
            check_result["value"] = str(value)
        if error:
            check_result["error"] = error

        self.results["checks"].append(check_result)

        # 更新摘要
        self.results["summary"]["total"] += 1
        if status == "pass":
            self.results["summary"]["passed"] += 1
        elif status == "fail":
            self.results["summary"]["failed"] += 1
        elif status == "warning":
            self.results["summary"]["warnings"] += 1
        elif status == "error":
            self.results["summary"]["errors"] = self.results["summary"].get("errors", 0) + 1

    def _validate_config_file(self, file_path: Path, config_type: str) -> Dict[str, Any]:
        """验证配置文件格式"""
        try:
            if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                return {"valid": True}
            elif file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return {"valid": True}
            else:
                return {"valid": True, "message": "非配置文件，跳过验证"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    # 私有检查方法
    def _check_python(self) -> Dict[str, Any]:
        """检查Python版本"""
        try:
            result = subprocess.run(
                ["python3", "--version"] if sys.platform != "win32" else ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip() or result.stderr.strip()
            # 提取版本号
            if "Python" in version_str:
                version = version_str.split("Python")[1].strip()
                major, minor = map(int, version.split('.')[:2])
                status = major >= 3 and minor >= 12
                return {
                    "status": status,
                    "version": version,
                    "message": f"Python {version} {'✓' if status else '✗ (需要 3.12+)'}"
                }
            return {"status": False, "version": version_str, "message": f"无法解析版本: {version_str}"}
        except Exception as e:
            return {"status": False, "version": None, "message": f"检查失败: {str(e)}"}

    def _check_nodejs(self) -> Dict[str, Any]:
        """检查Node.js版本"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip()
            if version_str.startswith("v"):
                version = version_str[1:]
                major = int(version.split('.')[0])
                status = major >= 22
                return {
                    "status": status,
                    "version": version,
                    "message": f"Node.js {version} {'✓' if status else '✗ (需要 22+)'}"
                }
            return {"status": False, "version": version_str, "message": f"无法解析版本: {version_str}"}
        except Exception as e:
            return {"status": False, "version": None, "message": f"检查失败: {str(e)}"}

    def _check_docker(self) -> Dict[str, Any]:
        """检查Docker"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip()
            return {
                "status": True,
                "version": version_str.split()[2].rstrip(','),
                "message": f"Docker 已安装: {version_str.split()[2]}"
            }
        except Exception as e:
            return {"status": False, "version": None, "message": f"Docker 未安装或不可用: {str(e)}"}

    def _check_docker_compose(self) -> Dict[str, Any]:
        """检查Docker Compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip()
            return {
                "status": True,
                "version": version_str,
                "message": f"Docker Compose 已安装: {version_str}"
            }
        except Exception as e:
            return {"status": False, "version": None, "message": f"Docker Compose 未安装: {str(e)}"}

    def _check_pnpm(self) -> Dict[str, Any]:
        """检查pnpm"""
        try:
            result = subprocess.run(
                ["pnpm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
            return {
                "status": True,
                "version": version,
                "message": f"pnpm {version}"
            }
        except Exception as e:
            return {"status": False, "version": None, "message": f"pnpm 未安装: {str(e)}"}

    def _check_uv(self) -> Dict[str, Any]:
        """检查uv"""
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip()
            version = version_str.split()[1] if len(version_str.split()) > 1 else version_str
            return {
                "status": True,
                "version": version,
                "message": f"uv {version}"
            }
        except Exception as e:
            return {"status": False, "version": None, "message": f"uv 未安装: {str(e)}"}

    def _check_git(self) -> Dict[str, Any]:
        """检查git"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip()
            return {
                "status": True,
                "version": version_str.split()[2],
                "message": f"git {version_str.split()[2]}"
            }
        except Exception as e:
            return {"status": False, "version": None, "message": f"git 未安装: {str(e)}"}

    def run_all_checks(self):
        """运行所有检查"""
        print("\n🚀 DeerFlow 生产部署验证工具")
        print("=" * 60)
        print(f"仓库根目录: {self.repo_root}")
        print(f"数据目录: {self.data_dir}")
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self.check_system_requirements()
        self.check_directories()
        self.check_config_files()
        self.check_environment_variables()
        self.check_docker_images()
        self.check_network_ports()

        return self.generate_report()

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DeerFlow 生产部署验证工具")
    parser.add_argument("--repo-root", default="/opt/deer-flow",
                       help="仓库根目录路径 (默认: /opt/deer-flow)")
    parser.add_argument("--data-dir", default="/data/deer-flow/.deer-flow",
                       help="数据目录路径 (默认: /data/deer-flow/.deer-flow)")
    parser.add_argument("--env-file", default=".env.production",
                       help="环境变量文件路径 (默认: .env.production)")

    args = parser.parse_args()

    # 加载环境变量文件
    if os.path.exists(args.env_file):
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
        print(f"✅ 已加载环境变量文件: {args.env_file}")
    else:
        print(f"⚠️  环境变量文件不存在: {args.env_file}")
        print("   将使用系统环境变量")

    validator = DeploymentValidator(
        repo_root=args.repo_root,
        data_dir=args.data_dir
    )

    report_file = validator.run_all_checks()

    # 返回退出码
    summary = validator.results["summary"]
    if summary.get("failed", 0) > 0 or summary.get("errors", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    # 尝试加载dotenv（如果可用）
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("⚠️  python-dotenv 未安装，环境变量文件加载功能不可用")
        print("   可以使用: uv add python-dotenv 安装")

    main()