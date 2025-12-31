import re
from dataclasses import dataclass
from jsonpath_ng import parse as jsonpath_parse

from app.engine.http_client import HttpResponse


@dataclass
class AssertionResult:
    """断言结果"""
    name: str
    passed: bool
    actual_value: str
    expected_value: str
    message: str


class AssertionEngine:
    """断言引擎"""

    # 支持的操作符
    OPERATORS = {
        "eq": lambda a, e: str(a) == str(e),
        "ne": lambda a, e: str(a) != str(e),
        "gt": lambda a, e: float(a) > float(e),
        "lt": lambda a, e: float(a) < float(e),
        "gte": lambda a, e: float(a) >= float(e),
        "lte": lambda a, e: float(a) <= float(e),
        "contains": lambda a, e: str(e) in str(a),
        "not_contains": lambda a, e: str(e) not in str(a),
        "regex": lambda a, e: bool(re.search(str(e), str(a))),
        "is_null": lambda a, e: a is None or str(a) == "",
        "is_not_null": lambda a, e: a is not None and str(a) != "",
    }

    OPERATOR_NAMES = {
        "eq": "等于",
        "ne": "不等于",
        "gt": "大于",
        "lt": "小于",
        "gte": "大于等于",
        "lte": "小于等于",
        "contains": "包含",
        "not_contains": "不包含",
        "regex": "匹配正则",
        "is_null": "为空",
        "is_not_null": "不为空",
    }

    def assert_one(
        self,
        response: HttpResponse,
        name: str,
        assertion_type: str,
        expression: str,
        operator: str,
        expected_value: str,
    ) -> AssertionResult:
        """
        执行单个断言

        Args:
            response: HTTP 响应对象
            name: 断言名称
            assertion_type: 断言类型 (status_code/json_path/header/response_time/contains)
            expression: 表达式
            operator: 操作符
            expected_value: 期望值

        Returns:
            AssertionResult 对象
        """
        try:
            # 获取实际值
            actual_value = self._get_actual_value(response, assertion_type, expression)

            # 执行比较
            op_func = self.OPERATORS.get(operator)
            if not op_func:
                return AssertionResult(
                    name=name,
                    passed=False,
                    actual_value=str(actual_value),
                    expected_value=expected_value,
                    message=f"不支持的操作符: {operator}",
                )

            try:
                passed = op_func(actual_value, expected_value)
            except (ValueError, TypeError) as e:
                return AssertionResult(
                    name=name,
                    passed=False,
                    actual_value=str(actual_value),
                    expected_value=expected_value,
                    message=f"比较失败: {str(e)}",
                )

            op_name = self.OPERATOR_NAMES.get(operator, operator)
            if passed:
                message = f"断言通过: {actual_value} {op_name} {expected_value}"
            else:
                message = f"断言失败: 实际值 [{actual_value}] {op_name} 期望值 [{expected_value}]"

            return AssertionResult(
                name=name,
                passed=passed,
                actual_value=str(actual_value) if actual_value is not None else "",
                expected_value=expected_value or "",
                message=message,
            )

        except Exception as e:
            return AssertionResult(
                name=name,
                passed=False,
                actual_value="",
                expected_value=expected_value or "",
                message=f"断言执行错误: {str(e)}",
            )

    def _get_actual_value(self, response: HttpResponse, assertion_type: str, expression: str):
        """获取断言的实际值"""
        if assertion_type == "status_code":
            return response.status_code

        elif assertion_type == "response_time":
            return response.duration_ms

        elif assertion_type == "header":
            for key, value in response.headers.items():
                if key.lower() == expression.lower():
                    return value
            return None

        elif assertion_type == "json_path":
            json_data = response.json
            if json_data is None:
                return None

            try:
                jsonpath_expr = jsonpath_parse(expression)
                matches = jsonpath_expr.find(json_data)
                if matches:
                    return matches[0].value
                return None
            except Exception:
                return None

        elif assertion_type == "contains":
            return response.body

        else:
            return None

    def assert_all(self, response: HttpResponse, assertions: list) -> list[AssertionResult]:
        """
        执行所有断言

        Args:
            response: HTTP 响应对象
            assertions: 断言配置列表

        Returns:
            AssertionResult 列表
        """
        results = []
        for assertion in assertions:
            result = self.assert_one(
                response=response,
                name=assertion.get("name", ""),
                assertion_type=assertion.get("type", ""),
                expression=assertion.get("expression", ""),
                operator=assertion.get("operator", "eq"),
                expected_value=assertion.get("expected_value", ""),
            )
            results.append(result)

        return results
