"""自定义工具单元测试"""

import json

import pytest

from deerflow.tools.custom_tools import CalculatorTool, WeatherTool, WebSearchTool


class TestWeatherTool:
    """天气查询工具测试"""

    def setup_method(self):
        """测试前准备"""
        self.tool = WeatherTool()

    def test_tool_initialization(self):
        """测试工具初始化"""
        assert self.tool.name == "get_weather"
        assert "天气" in self.tool.description
        assert self.tool.args_schema is not None

    def test_get_weather_celsius(self):
        """测试获取摄氏度天气"""
        result = self.tool._run(city="北京", units="celsius")
        data = json.loads(result)

        assert "city" in data
        assert data["city"] == "北京"
        assert data["units"] == "celsius"
        assert "temperature" in data
        assert data["temperature"] == 25

    def test_get_weather_fahrenheit(self):
        """测试获取华氏度天气"""
        result = self.tool._run(city="纽约", units="fahrenheit")
        data = json.loads(result)

        assert data["city"] == "纽约"
        assert data["units"] == "fahrenheit"
        assert data["temperature"] == 77

    def test_get_weather_default_units(self):
        """测试默认单位"""
        result = self.tool._run(city="上海")
        data = json.loads(result)

        assert data["units"] == "celsius"

    def test_get_weather_has_all_fields(self):
        """测试返回的数据字段完整"""
        result = self.tool._run(city="广州")
        data = json.loads(result)

        required_fields = ["city", "temperature", "weather", "humidity", "wind_speed", "visibility", "pressure"]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"


class TestCalculatorTool:
    """计算器工具测试"""

    def setup_method(self):
        """测试前准备"""
        self.tool = CalculatorTool()

    def test_tool_initialization(self):
        """测试工具初始化"""
        assert self.tool.name == "calculator"
        assert "计算" in self.tool.description

    def test_basic_addition(self):
        """测试基本加法"""
        result = self.tool._run(expression="2 + 3")
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 5
        assert data["expression"] == "2 + 3"

    def test_complex_expression(self):
        """测试复杂表达式"""
        result = self.tool._run(expression="2 + 3 * 4")
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 14  # 2 + (3 * 4) = 14

    def test_square_root(self):
        """测试平方根"""
        result = self.tool._run(expression="sqrt(16)")
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 4.0

    def test_power_function(self):
        """测试幂函数"""
        result = self.tool._run(expression="pow(2, 3)")
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 8

    def test_precision(self):
        """测试精度设置"""
        result = self.tool._run(expression="1/3", precision=4)
        data = json.loads(result)

        assert data["success"] is True
        assert data["precision"] == 4
        # 1/3 四舍五入到 4 位小数
        assert data["result"] == round(1 / 3, 4)

    def test_invalid_expression(self):
        """测试无效表达式"""
        result = self.tool._run(expression="invalid_function()")
        data = json.loads(result)

        assert data["success"] is False
        assert "error" in data

    def test_division_by_zero(self):
        """测试除以零"""
        result = self.tool._run(expression="1/0")
        data = json.loads(result)

        assert data["success"] is False


class TestWebSearchTool:
    """网页查询工具测试"""

    def setup_method(self):
        """测试前准备"""
        self.tool = WebSearchTool()

    def test_tool_initialization(self):
        """测试工具初始化"""
        assert self.tool.name == "web_search"
        assert "搜索" in self.tool.description

    def test_web_search_default(self):
        """测试默认搜索"""
        result = self.tool._run(query="Python")
        data = json.loads(result)

        assert data["query"] == "Python"
        assert "results" in data
        assert len(data["results"]) == 5  # 默认返回 5 个结果

    def test_web_search_custom_max_results(self):
        """测试自定义结果数量"""
        result = self.tool._run(query="AI", max_results=3)
        data = json.loads(result)

        assert data["query"] == "AI"
        assert len(data["results"]) == 3

    def test_web_search_result_structure(self):
        """测试搜索结果结构"""
        result = self.tool._run(query="深度学习", max_results=1)
        data = json.loads(result)

        assert len(data["results"]) > 0
        result_item = data["results"][0]

        required_fields = ["title", "description", "url", "relevance_score"]
        for field in required_fields:
            assert field in result_item, f"缺少字段: {field}"

    def test_web_search_max_results_limit(self):
        """测试最大结果数限制"""
        result = self.tool._run(query="测试", max_results=100)
        data = json.loads(result)

        # 应该限制在 5 个以内
        assert len(data["results"]) <= 5

    def test_web_search_empty_query(self):
        """测试空查询"""
        # 这应该返回结果，虽然查询是空的
        result = self.tool._run(query="")
        data = json.loads(result)

        # 即使查询为空，也应该返回结果列表
        assert "results" in data


class TestToolIntegration:
    """工具集成测试"""

    def test_all_tools_available(self):
        """测试所有工具都可用"""
        weather = WeatherTool()
        calculator = CalculatorTool()
        search = WebSearchTool()

        assert weather.name == "get_weather"
        assert calculator.name == "calculator"
        assert search.name == "web_search"

    def test_tools_have_descriptions(self):
        """测试所有工具都有描述"""
        tools = [WeatherTool(), CalculatorTool(), WebSearchTool()]

        for tool in tools:
            assert tool.description is not None
            assert len(tool.description) > 0

    def test_tools_have_schemas(self):
        """测试所有工具都有输入模式"""
        tools = [WeatherTool(), CalculatorTool(), WebSearchTool()]

        for tool in tools:
            assert tool.args_schema is not None

    def test_tools_async_methods_exist(self):
        """测试所有工具都有异步方法"""
        tools = [WeatherTool(), CalculatorTool(), WebSearchTool()]

        for tool in tools:
            assert hasattr(tool, "_arun")
            assert callable(getattr(tool, "_arun"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
