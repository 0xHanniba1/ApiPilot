import re
from dataclasses import dataclass
from jsonpath_ng import parse as jsonpath_parse

from app.engine.http_client import HttpResponse


@dataclass
class ExtractResult:
    """提取结果"""
    variable_name: str
    value: str | None
    success: bool
    error: str = None


class ExtractorEngine:
    """提取器引擎"""

    def extract(
        self,
        response: HttpResponse,
        source: str,
        expression: str,
        variable_name: str,
        default_value: str = None,
    ) -> ExtractResult:
        """
        从响应中提取值

        Args:
            response: HTTP 响应对象
            source: 提取来源 (body/header/cookie)
            expression: 提取表达式 (JSONPath 或键名)
            variable_name: 保存到的变量名
            default_value: 默认值

        Returns:
            ExtractResult 对象
        """
        try:
            if source == "body":
                value = self._extract_from_body(response, expression)
            elif source == "header":
                value = self._extract_from_header(response, expression)
            elif source == "cookie":
                value = self._extract_from_cookie(response, expression)
            else:
                return ExtractResult(
                    variable_name=variable_name,
                    value=default_value,
                    success=False,
                    error=f"不支持的提取来源: {source}",
                )

            # 如果提取失败，使用默认值
            if value is None:
                value = default_value

            return ExtractResult(
                variable_name=variable_name,
                value=value,
                success=True,
            )

        except Exception as e:
            return ExtractResult(
                variable_name=variable_name,
                value=default_value,
                success=False,
                error=str(e),
            )

    def _extract_from_body(self, response: HttpResponse, expression: str) -> str | None:
        """从响应体提取（支持 JSONPath）"""
        if not response.body:
            return None

        # 尝试 JSONPath 提取
        if expression.startswith("$"):
            json_data = response.json
            if json_data is None:
                return None

            try:
                jsonpath_expr = jsonpath_parse(expression)
                matches = jsonpath_expr.find(json_data)
                if matches:
                    value = matches[0].value
                    return str(value) if value is not None else None
                return None
            except Exception:
                return None

        # 正则表达式提取
        if expression.startswith("/") and expression.endswith("/"):
            pattern = expression[1:-1]
            match = re.search(pattern, response.body)
            if match:
                return match.group(1) if match.groups() else match.group(0)
            return None

        # 直接返回整个响应体（如果表达式为空）
        if not expression or expression == ".":
            return response.body

        return None

    def _extract_from_header(self, response: HttpResponse, expression: str) -> str | None:
        """从响应头提取"""
        if not response.headers:
            return None

        # 不区分大小写查找
        for key, value in response.headers.items():
            if key.lower() == expression.lower():
                return value

        return None

    def _extract_from_cookie(self, response: HttpResponse, expression: str) -> str | None:
        """从 Cookie 提取"""
        if not response.cookies:
            return None

        return response.cookies.get(expression)

    def extract_all(self, response: HttpResponse, extractors: list) -> dict:
        """
        执行所有提取器

        Args:
            response: HTTP 响应对象
            extractors: 提取器配置列表

        Returns:
            提取结果字典 {variable_name: value}
        """
        results = {}
        for ext in extractors:
            result = self.extract(
                response=response,
                source=ext.get("source", "body"),
                expression=ext.get("expression", ""),
                variable_name=ext.get("variable_name", ""),
                default_value=ext.get("default_value"),
            )
            if result.value is not None:
                results[result.variable_name] = result.value

        return results
