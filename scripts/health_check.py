#!/usr/bin/env python3
"""
DeerFlow 健康检查工具
检查所有服务的运行状态和健康状况
"""

import os
import sys
import json
import asyncio
import aiohttp
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class HealthChecker:
    """DeerFlow 健康检查器"""

    def __init__(self, base_url: str = "http://localhost:2026"):
        self.base_url = base_url.rstrip('/')
        self.services = {
            "frontend": f"{self.base_url}",
            "backend": f"{self.base_url.replace(':2026', ':8001')}",
            "langgraph": f"{self.base_url.replace(':2026', ':2024')}",
        }
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "services": {},
            "checks": []
        }

    async def check_service_health(self, service_name: str, url: str) -> Dict[str, Any]:
        """检查单个服务的健康状态"""
        result = {
            "service": service_name,
            "url": url,
            "status": "unknown",
            "response_time": None,
            "details": {}
        }

        try:
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (datetime.now() - start_time).total_seconds()
                    result["response_time"] = round(response_time, 3)

                    if response.status == 200:
                        result["status"] = "healthy"
                        try:
                            result["details"] = await response.json()
                        except:
                            result["details"] = {"message": "OK"}
                    else:
                        result["status"] = "unhealthy"
                        result["details"] = {
                            "status_code": response.status,
                            "reason": response.reason
                        }

        except aiohttp.ClientError as e:
            result["status"] = "unreachable"
            result["details"] = {"error": str(e)}
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["details"] = {"error": "Request timeout"}
        except Exception as e:
            result["status"] = "error"
            result["details"] = {"error": str(e)}

        return result

    async def check_all_services(self) -> List[Dict[str, Any]]:
        """并发检查所有服务"""
        tasks = []
        for service_name, url in self.services.items():
            tasks.append(self.check_service_health(service_name, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                service_name = list(self.services.keys())[i]
                processed_results.append({
                    "service": service_name,
                    "url": self.services[service_name],
                    "status": "error",
                    "response_time": None,
                    "details": {"error": str(result)}
                })
            else:
                processed_results.append(result)

        return processed_results

    def check_docker_containers(self) -> List[Dict[str, Any]]:
        """检查Docker容器状态"""
        containers = [
            "deer-flow-nginx",
            "deer-flow-frontend",
            "deer-flow-gateway",
            "deer-flow-langgraph",
            "deer-flow-postgres",
            "deer-flow-redis"
        ]

        results = []
        try:
            # 检查Docker是否运行
            subprocess.run(["docker", "ps"], capture_output=True, check=True, timeout=5)

            for container in containers:
                result = {
                    "container": container,
                    "status": "unknown",
                    "details": {}
                }

                try:
                    # 检查容器是否运行
                    inspect_cmd = ["docker", "inspect", "--format", "{{.State.Running}}", container]
                    running = subprocess.run(
                        inspect_cmd,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if running.returncode == 0:
                        is_running = running.stdout.strip() == "true"
                        result["status"] = "running" if is_running else "stopped"

                        # 获取容器详细信息
                        detail_cmd = ["docker", "inspect", "--format", "{{json .}}", container]
                        detail = subprocess.run(
                            detail_cmd,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )

                        if detail.returncode == 0:
                            import json
                            try:
                                container_info = json.loads(detail.stdout)
                                result["details"] = {
                                    "status": container_info.get("State", {}).get("Status", "unknown"),
                                    "started_at": container_info.get("State", {}).get("StartedAt", ""),
                                    "restart_count": container_info.get("RestartCount", 0),
                                    "image": container_info.get("Config", {}).get("Image", "")
                                }
                            except json.JSONDecodeError:
                                result["details"] = {"error": "Failed to parse container info"}
                    else:
                        result["status"] = "not_found"
                        result["details"] = {"error": "Container not found"}

                except subprocess.TimeoutExpired:
                    result["status"] = "timeout"
                    result["details"] = {"error": "Docker command timeout"}
                except Exception as e:
                    result["status"] = "error"
                    result["details"] = {"error": str(e)}

                results.append(result)

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Docker未安装或未运行
            for container in containers:
                results.append({
                    "container": container,
                    "status": "docker_unavailable",
                    "details": {"error": "Docker is not available"}
                })

        return results

    def check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            result = subprocess.run(
                ["df", "-h", self.repo_root],
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    return {
                        "filesystem": parts[0],
                        "size": parts[1],
                        "used": parts[2],
                        "available": parts[3],
                        "use_percent": parts[4],
                        "mount_point": parts[5] if len(parts) > 5 else ""
                    }

        except Exception as e:
            return {"error": str(e)}

        return {"error": "Failed to parse disk space"}

    def check_memory_usage(self) -> Dict[str, Any]:
        """检查内存使用"""
        try:
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith("Mem:"):
                    parts = line.split()
                    if len(parts) >= 7:
                        return {
                            "total": parts[1],
                            "used": parts[2],
                            "free": parts[3],
                            "shared": parts[4],
                            "buff_cache": parts[5],
                            "available": parts[6]
                        }

        except Exception as e:
            return {"error": str(e)}

        return {"error": "Failed to parse memory usage"}

    def print_results(self):
        """打印检查结果"""
        print("=" * 60)
        print("🏥 DeerFlow 健康检查报告")
        print("=" * 60)
        print(f"检查时间: {self.results['timestamp']}")
        print()

        # 服务状态
        print("📊 服务状态:")
        print("-" * 40)

        healthy_count = 0
        total_count = len(self.results["services"])

        for service_name, service_info in self.results["services"].items():
            status = service_info["status"]
            url = service_info["url"]

            if status == "healthy":
                symbol = "✅"
                healthy_count += 1
            elif status in ["unhealthy", "unreachable", "timeout", "error"]:
                symbol = "❌"
            else:
                symbol = "❓"

            response_time = service_info.get("response_time", "N/A")
            if response_time:
                print(f"{symbol} {service_name:12} {status:12} {url:30} ({response_time}s)")
            else:
                print(f"{symbol} {service_name:12} {status:12} {url:30}")

        print()

        # Docker容器状态
        if "docker_containers" in self.results:
            print("🐳 Docker 容器状态:")
            print("-" * 40)

            for container in self.results["docker_containers"]:
                status = container["status"]
                if status == "running":
                    symbol = "✅"
                elif status in ["stopped", "not_found", "docker_unavailable"]:
                    symbol = "⚠️"
                else:
                    symbol = "❌"

                print(f"{symbol} {container['container']:25} {status}")

            print()

        # 系统资源
        print("💻 系统资源:")
        print("-" * 40)

        if "disk_space" in self.results:
            disk = self.results["disk_space"]
            if "error" not in disk:
                print(f"💾 磁盘: {disk['used']}/{disk['size']} ({disk['use_percent']}) 可用: {disk['available']}")
            else:
                print(f"💾 磁盘: 检查失败 - {disk['error']}")

        if "memory_usage" in self.results:
            memory = self.results["memory_usage"]
            if "error" not in memory:
                print(f"🧠 内存: {memory['used']}/{memory['total']} 可用: {memory['available']}")
            else:
                print(f"🧠 内存: 检查失败 - {memory['error']}")

        print()

        # 总结
        print("=" * 60)
        print("📈 总结:")
        print("-" * 40)

        if healthy_count == total_count and total_count > 0:
            print("🎉 所有服务都正常运行！")
            self.results["overall_status"] = "healthy"
        elif healthy_count > 0:
            print(f"⚠️  {healthy_count}/{total_count} 个服务正常运行，部分服务有问题")
            self.results["overall_status"] = "degraded"
        else:
            print("❌ 所有服务都不可用！")
            self.results["overall_status"] = "unhealthy"

        print("=" * 60)

    def save_report(self, filename: str = None) -> str:
        """保存检查报告为JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_check_{timestamp}.json"

        report_file = Path("logs") / filename
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细报告已保存到: {report_file}")
        return str(report_file)

async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DeerFlow 健康检查工具")
    parser.add_argument("--url", default="http://localhost:2026",
                       help="基础URL (默认: http://localhost:2026)")
    parser.add_argument("--save", action="store_true",
                       help="保存检查报告到文件")
    parser.add_argument("--output", default=None,
                       help="输出文件名 (与--save一起使用)")

    args = parser.parse_args()

    checker = HealthChecker(base_url=args.url)

    print("🔍 正在检查服务健康状况...")
    print()

    # 检查HTTP服务
    services_results = await checker.check_all_services()
    checker.results["services"] = {
        result["service"]: result for result in services_results
    }

    # 检查Docker容器
    checker.results["docker_containers"] = checker.check_docker_containers()

    # 检查系统资源
    checker.results["disk_space"] = checker.check_disk_space()
    checker.results["memory_usage"] = checker.check_memory_usage()

    # 打印结果
    checker.print_results()

    # 保存报告
    if args.save:
        checker.save_report(args.output)

    # 返回退出码
    if checker.results["overall_status"] in ["healthy", "degraded"]:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)