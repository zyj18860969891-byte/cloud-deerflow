"""自定义工具示例 - WeatherTool (天气查询工具)

演示如何创建和使用自定义工具。
"""

import json
import logging

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WeatherInput(BaseModel):
    """天气查询工具的输入参数"""

    city: str = Field(..., description="城市名称，例如: 北京, 上海")
    units: str = Field(default="celsius", description="温度单位: celsius (摄氏度) 或 fahrenheit (华氏度)")


class WeatherTool(BaseTool):
    """天气查询工具 - 获取城市天气信息"""

    name: str = "get_weather"
    description: str = "获取指定城市的天气信息。支持全球主要城市，返回温度、天气状况、湿度等信息。"
    args_schema: type = WeatherInput

    def _run(self, city: str, units: str = "celsius") -> str:
        """
        执行天气查询

        Args:
            city: 城市名称
            units: 温度单位

        Returns:
            天气信息的 JSON 字符串
        """
        try:
            # 模拟 API 调用 (实际应用中应调用真实的天气 API，如 OpenWeather)
            weather_data = {
                "city": city,
                "temperature": 25 if units == "celsius" else 77,
                "units": units,
                "weather": "晴朗",
                "humidity": 65,
                "wind_speed": "5 km/h",
                "visibility": "10 km",
                "pressure": "1013 hPa",
                "timestamp": "2026-04-01T12:00:00Z",
            }

            logger.info(f"获取天气信息: {city}, 单位: {units}")
            return json.dumps(weather_data, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"天气查询失败: {str(e)}")
            return json.dumps({"error": "天气查询失败", "details": str(e), "city": city}, ensure_ascii=False)

    async def _arun(self, city: str, units: str = "celsius") -> str:
        """异步版本"""
        return self._run(city, units)


class CalculatorInput(BaseModel):
    """计算器工具的输入参数"""

    expression: str = Field(..., description="数学表达式，例如: 2 + 3 * 4, sqrt(16)")
    precision: int = Field(default=2, description="结果精度（小数位数）")


class CalculatorTool(BaseTool):
    """数学计算工具 - 执行数学表达式计算"""

    name: str = "calculator"
    description: str = "执行数学计算。支持基本算术运算、三角函数、平方根等。安全的表达式评估。"
    args_schema: type = CalculatorInput

    # 允许的函数和常量
    ALLOWED_NAMES: set = {"abs", "round", "min", "max", "sum", "pow", "sqrt", "sin", "cos", "tan", "log", "exp", "pi", "e"}

    def _run(self, expression: str, precision: int = 2) -> str:
        """
        执行数学计算

        Args:
            expression: 数学表达式
            precision: 结果精度

        Returns:
            计算结果的 JSON 字符串
        """
        try:
            import math

            # 构建安全的命名空间
            namespace = {
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "exp": math.exp,
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "pi": math.pi,
                "e": math.e,
            }

            # 安全地评估表达式
            result = eval(expression, {"__builtins__": {}}, namespace)

            # 格式化结果
            if isinstance(result, float):
                result = round(result, precision)

            logger.info(f"计算表达式: {expression} = {result}")

            return json.dumps({"expression": expression, "result": result, "precision": precision, "success": True}, ensure_ascii=False)

        except Exception as e:
            logger.error(f"计算失败: {str(e)}")
            return json.dumps({"expression": expression, "error": "计算失败", "details": str(e), "success": False}, ensure_ascii=False)

    async def _arun(self, expression: str, precision: int = 2) -> str:
        """异步版本"""
        return self._run(expression, precision)


class WebSearchInput(BaseModel):
    """网页查询工具的输入参数"""

    query: str = Field(..., description="搜索查询词")
    max_results: int = Field(default=5, description="返回的最大结果数")


class WebSearchTool(BaseTool):
    """网页查询工具 - 搜索并返回网页内容摘要"""

    name: str = "web_search"
    description: str = "搜索网页内容。根据查询词返回相关页面的摘要信息，包括标题、描述和URL。"
    args_schema: type = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        """
        执行网页搜索

        Args:
            query: 搜索查询词
            max_results: 最大结果数

        Returns:
            搜索结果的 JSON 字符串
        """
        try:
            # 模拟搜索结果 (实际应用中应调用真实的搜索 API，如 Google Search API)
            results = [
                {"title": f"关于 '{query}' 的搜索结果 {i + 1}", "description": f"这是关于 {query} 的相关内容摘要。", "url": f"https://example.com/result/{i + 1}", "relevance_score": 0.9 - (i * 0.1)} for i in range(min(max_results, 5))
            ]

            logger.info(f"网页搜索: {query}, 返回 {len(results)} 个结果")

            return json.dumps({"query": query, "results": results, "total_results": len(results)}, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"网页搜索失败: {str(e)}")
            return json.dumps({"query": query, "error": "搜索失败", "details": str(e)}, ensure_ascii=False)

    async def _arun(self, query: str, max_results: int = 5) -> str:
        """异步版本"""
        return self._run(query, max_results)


# 导出工具类供注册使用
__all__ = [
    "WeatherTool",
    "CalculatorTool",
    "WebSearchTool",
]
