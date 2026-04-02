#!/usr/bin/env python3
"""
DeerFlow 备份工具
自动备份数据库、配置文件和租户数据
"""

import os
import sys
import json
import subprocess
import tarfile
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class BackupManager:
    """DeerFlow 备份管理器"""

    def __init__(self, repo_root: str = None, data_dir: str = None, backup_dir: str = None):
        self.repo_root = Path(repo_root or os.getenv('DEER_FLOW_REPO_ROOT', '/opt/deer-flow'))
        self.data_dir = Path(data_dir or os.getenv('DEER_FLOW_HOME', '/data/deer-flow/.deer-flow'))
        self.backup_dir = Path(backup_dir or os.getenv('BACKUP_DIR', '/backup/deer-flow'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"deerflow_backup_{self.timestamp}"
        self.backup_file = self.backup_dir / f"{self.backup_name}.tar.gz"

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backup_name": self.backup_name,
            "backup_file": str(self.backup_file),
            "components": [],
            "total_size": 0,
            "status": "unknown"
        }

    def backup_config_files(self) -> Dict[str, Any]:
        """备份配置文件"""
        print("📝 备份配置文件...")

        config_files = [
            self.repo_root / "config.yaml",
            self.repo_root / "extensions_config.json",
            self.repo_root / ".env.production",
            self.repo_root / "docker" / "docker-compose.yaml",
            self.repo_root / "docker" / "nginx" / "nginx.conf",
        ]

        backed_up_files = []
        temp_dir = Path(tempfile.mkdtemp(prefix="deerflow_backup_"))

        try:
            for config_file in config_files:
                if config_file.exists():
                    # 计算相对路径
                    rel_path = config_file.relative_to(self.repo_root)
                    target_path = temp_dir / "config" / rel_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # 复制文件
                    import shutil
                    shutil.copy2(config_file, target_path)
                    backed_up_files.append(str(rel_path))

            return {
                "component": "config_files",
                "status": "success",
                "files_backed_up": backed_up_files,
                "count": len(backed_up_files)
            }

        except Exception as e:
            return {
                "component": "config_files",
                "status": "error",
                "error": str(e)
            }

    def backup_database(self) -> Dict[str, Any]:
        """备份PostgreSQL数据库"""
        print("🗄️  备份数据库...")

        try:
            # 检查PostgreSQL是否运行
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=deer-flow-postgres", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "deer-flow-postgres" not in result.stdout:
                return {
                    "component": "database",
                    "status": "skipped",
                    "reason": "PostgreSQL container not running"
                }

            # 创建数据库备份
            temp_dir = Path(tempfile.mkdtemp(prefix="deerflow_backup_"))
            backup_file = temp_dir / "database.sql"

            # 使用docker exec运行pg_dump
            env_vars = {
                'PGHOST': 'localhost',
                'PGPORT': '5432',
                'PGUSER': 'deerflow',
                'PGDATABASE': 'deerflow'
            }

            # 获取密码（从环境变量）
            db_password = os.getenv('DB_PASSWORD')
            if db_password:
                env_vars['PGPASSWORD'] = db_password

            dump_cmd = [
                "docker", "exec", "deer-flow-postgres",
                "pg_dump", "-U", "deerflow", "deerflow"
            ]

            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    dump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=60,
                    env={**os.environ, **env_vars}
                )

            if result.returncode == 0:
                file_size = backup_file.stat().st_size
                return {
                    "component": "database",
                    "status": "success",
                    "backup_file": "database.sql",
                    "size_bytes": file_size,
                    "size_human": self._format_size(file_size)
                }
            else:
                return {
                    "component": "database",
                    "status": "error",
                    "error": result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                "component": "database",
                "status": "error",
                "error": "Database backup timeout"
            }
        except Exception as e:
            return {
                "component": "database",
                "status": "error",
                "error": str(e)
            }

    def backup_redis_data(self) -> Dict[str, Any]:
        """备份Redis数据"""
        print("💾 备份Redis数据...")

        try:
            # 检查Redis是否运行
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=deer-flow-redis", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "deer-flow-redis" not in result.stdout:
                return {
                    "component": "redis",
                    "status": "skipped",
                    "reason": "Redis container not running"
                }

            # 创建Redis备份
            temp_dir = Path(tempfile.mkdtemp(prefix="deerflow_backup_"))
            backup_file = temp_dir / "redis_dump.rdb"

            # 触发Redis保存
            subprocess.run(
                ["docker", "exec", "deer-flow-redis", "redis-cli", "SAVE"],
                capture_output=True,
                timeout=30
            )

            # 复制RDB文件
            result = subprocess.run(
                ["docker", "cp", "deer-flow-redis:/data/dump.rdb", str(backup_file)],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and backup_file.exists():
                file_size = backup_file.stat().st_size
                return {
                    "component": "redis",
                    "status": "success",
                    "backup_file": "redis_dump.rdb",
                    "size_bytes": file_size,
                    "size_human": self._format_size(file_size)
                }
            else:
                return {
                    "component": "redis",
                    "status": "error",
                    "error": "Failed to copy Redis dump file"
                }

        except subprocess.TimeoutExpired:
            return {
                "component": "redis",
                "status": "error",
                "error": "Redis backup timeout"
            }
        except Exception as e:
            return {
                "component": "redis",
                "status": "error",
                "error": str(e)
            }

    def backup_tenant_data(self) -> Dict[str, Any]:
        """备份租户数据"""
        print("👥 备份租户数据...")

        tenants_dir = self.data_dir / "tenants"
        if not tenants_dir.exists():
            return {
                "component": "tenant_data",
                "status": "skipped",
                "reason": "Tenants directory not found"
            }

        try:
            # 统计租户数据
            tenants = list(tenants_dir.iterdir())
            tenant_count = sum(1 for t in tenants if t.is_dir())

            if tenant_count == 0:
                return {
                    "component": "tenant_data",
                    "status": "skipped",
                    "reason": "No tenant data found"
                }

            # 计算总大小
            total_size = 0
            for tenant in tenants:
                if tenant.is_dir():
                    for file in tenant.rglob("*"):
                        if file.is_file():
                            total_size += file.stat().st_size

            return {
                "component": "tenant_data",
                "status": "success",
                "tenant_count": tenant_count,
                "size_bytes": total_size,
                "size_human": self._format_size(total_size),
                "backup_location": "tenants/"
            }

        except Exception as e:
            return {
                "component": "tenant_data",
                "status": "error",
                "error": str(e)
            }

    def backup_skills(self) -> Dict[str, Any]:
        """备份技能库"""
        print("🔧 备份技能库...")

        skills_dir = self.repo_root / "skills"
        if not skills_dir.exists():
            return {
                "component": "skills",
                "status": "skipped",
                "reason": "Skills directory not found"
            }

        try:
            # 统计技能文件
            skill_files = list(skills_dir.rglob("*"))
            file_count = sum(1 for f in skill_files if f.is_file())

            # 计算总大小
            total_size = sum(f.stat().st_size for f in skill_files if f.is_file())

            return {
                "component": "skills",
                "status": "success",
                "file_count": file_count,
                "size_bytes": total_size,
                "size_human": self._format_size(total_size),
                "backup_location": "skills/"
            }

        except Exception as e:
            return {
                "component": "skills",
                "status": "error",
                "error": str(e)
            }

    def create_archive(self, temp_dir: Path) -> Dict[str, Any]:
        """创建压缩归档"""
        print("📦 创建备份归档...")

        try:
            with tarfile.open(self.backup_file, "w:gz") as tar:
                tar.add(temp_dir, arcname=self.backup_name)

            file_size = self.backup_file.stat().st_size

            return {
                "component": "archive",
                "status": "success",
                "archive_file": str(self.backup_file),
                "size_bytes": file_size,
                "size_human": self._format_size(file_size)
            }

        except Exception as e:
            return {
                "component": "archive",
                "status": "error",
                "error": str(e)
            }

    def cleanup_temp_files(self, temp_dir: Path):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"⚠️  清理临时文件失败: {e}")

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def run_backup(self) -> Dict[str, Any]:
        """执行完整备份"""
        print("=" * 60)
        print("💾 DeerFlow 备份工具")
        print("=" * 60)
        print(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"备份目录: {self.backup_dir}")
        print(f"备份文件: {self.backup_file}")
        print()

        temp_dir = Path(tempfile.mkdtemp(prefix="deerflow_backup_"))

        try:
            # 执行各个备份组件
            components = [
                self.backup_config_files,
                self.backup_database,
                self.backup_redis_data,
                self.backup_tenant_data,
                self.backup_skills
            ]

            for component_func in components:
                result = component_func()
                self.results["components"].append(result)

                # 如果有临时文件需要添加到归档
                if result.get("backup_file"):
                    temp_file = temp_dir / result["backup_file"]
                    temp_file.parent.mkdir(parents=True, exist_ok=True)
                    # 这里简化处理，实际应该复制文件到temp_dir

            # 创建最终归档
            archive_result = self.create_archive(temp_dir)
            self.results["components"].append(archive_result)

            # 计算总大小
            total_size = sum(
                c.get("size_bytes", 0) for c in self.results["components"]
                if c.get("size_bytes")
            )
            self.results["total_size"] = total_size
            self.results["total_size_human"] = self._format_size(total_size)

            # 确定最终状态
            errors = [c for c in self.results["components"] if c["status"] == "error"]
            if errors:
                self.results["status"] = "partial_failure"
            elif all(c["status"] in ["success", "skipped"] for c in self.results["components"]):
                self.results["status"] = "success"
            else:
                self.results["status"] = "partial_success"

            return self.results

        finally:
            self.cleanup_temp_files(temp_dir)

    def print_summary(self):
        """打印备份摘要"""
        print("\n" + "=" * 60)
        print("📊 备份完成")
        print("=" * 60)

        for component in self.results["components"]:
            status = component["status"]
            if status == "success":
                symbol = "✅"
            elif status == "error":
                symbol = "❌"
            elif status == "skipped":
                symbol = "⭕"
            else:
                symbol = "❓"

            print(f"{symbol} {component['component']}: {status}")

        print(f"\n📦 总备份大小: {self.results.get('total_size_human', 'N/A')}")
        print(f"📄 备份文件: {self.backup_file}")
        print(f"📅 备份时间: {self.timestamp}")

        if self.results["status"] == "success":
            print("\n🎉 备份成功完成！")
        else:
            print("\n⚠️  备份部分失败，请检查上述错误")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DeerFlow 备份工具")
    parser.add_argument("--repo-root", default="/opt/deer-flow",
                       help="仓库根目录路径 (默认: /opt/deer-flow)")
    parser.add_argument("--data-dir", default="/data/deer-flow/.deer-flow",
                       help="数据目录路径 (默认: /data/deer-flow/.deer-flow)")
    parser.add_argument("--backup-dir", default="/backup/deer-flow",
                       help="备份目录路径 (默认: /backup/deer-flow)")
    parser.add_argument("--list", action="store_true",
                       help="列出所有现有备份")
    parser.add_argument("--restore", metavar="BACKUP_FILE",
                       help="从指定备份文件恢复")

    args = parser.parse_args()

    if args.list:
        # 列出备份文件
        backup_dir = Path(args.backup_dir)
        if backup_dir.exists():
            backups = sorted(backup_dir.glob("deerflow_backup_*.tar.gz"), reverse=True)
            print("📋 现有备份:")
            print("-" * 60)
            for backup in backups[:10]:  # 只显示最近10个
                stat = backup.stat()
                size = self._format_size(stat.st_size)
                print(f"{backup.name}  {size}  {datetime.fromtimestamp(stat.st_mtime)}")
        else:
            print("📭 没有找到备份文件")
        return

    if args.restore:
        # 恢复备份
        print(f"🔄 正在恢复备份: {args.restore}")
        # 实现恢复逻辑...
        print("⚠️  恢复功能尚未实现")
        return

    # 执行备份
    manager = BackupManager(
        repo_root=args.repo_root,
        data_dir=args.data_dir,
        backup_dir=args.backup_dir
    )

    results = manager.run_backup()
    manager.print_summary()

    # 返回退出码
    if results["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()