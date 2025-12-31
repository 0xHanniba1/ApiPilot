from dataclasses import dataclass, field

from app.engine.variable import VariableEngine
from app.engine.http_client import HttpClient, HttpResponse
from app.engine.extractor import ExtractorEngine
from app.engine.assertion import AssertionEngine, AssertionResult


@dataclass
class ExecutionResult:
    """用例执行结果"""
    status: str  # passed/failed/error
    request_url: str = ""
    request_method: str = ""
    request_headers: dict = field(default_factory=dict)
    request_body: str = ""
    response_status_code: int = 0
    response_headers: dict = field(default_factory=dict)
    response_body: str = ""
    duration_ms: int = 0
    assertion_results: list = field(default_factory=list)
    extractor_results: dict = field(default_factory=dict)
    error_message: str = ""


class TestExecutor:
    """测试用例执行器"""

    def __init__(self):
        self.http_client = HttpClient()
        self.extractor_engine = ExtractorEngine()
        self.assertion_engine = AssertionEngine()

    async def execute(
        self,
        base_url: str,
        test_case: dict,
        env_vars: dict = None,
        extracted_vars: dict = None,
    ) -> ExecutionResult:
        """
        执行单个测试用例

        Args:
            base_url: 环境基础 URL
            test_case: 测试用例配置
            env_vars: 环境变量
            extracted_vars: 已提取的变量（用于用例间传递）

        Returns:
            ExecutionResult 对象
        """
        # 初始化变量引擎
        var_engine = VariableEngine(env_vars=env_vars, extracted_vars=extracted_vars)

        try:
            # 1. 变量替换
            url = self._build_url(base_url, test_case.get("path", ""), var_engine)
            method = test_case.get("method", "GET")
            headers = var_engine.render_dict(test_case.get("headers", {}))
            params = var_engine.render_dict(test_case.get("params", {}))
            body_type = test_case.get("body_type", "none")
            body_content = None

            if body_type == "json":
                body_content = var_engine.render_json(test_case.get("body_content", ""))
            elif body_type in ("form", "form-data", "raw"):
                body_content = var_engine.render(test_case.get("body_content", ""))

            # 2. 发送 HTTP 请求
            self.http_client.timeout = test_case.get("timeout", 30)
            response = await self.http_client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                body_type=body_type,
                body_content=body_content,
            )

            # 检查请求错误
            if response.error:
                return ExecutionResult(
                    status="error",
                    request_url=url,
                    request_method=method,
                    request_headers=headers,
                    request_body=body_content or "",
                    duration_ms=response.duration_ms,
                    error_message=response.error,
                )

            # 3. 执行提取器
            extractors = test_case.get("extractors", [])
            extractor_results = {}
            if extractors:
                extractor_configs = [
                    {
                        "source": e.get("source", "body"),
                        "expression": e.get("expression", ""),
                        "variable_name": e.get("variable_name", ""),
                        "default_value": e.get("default_value"),
                    }
                    for e in extractors
                ]
                extractor_results = self.extractor_engine.extract_all(response, extractor_configs)

            # 4. 执行断言
            assertions = test_case.get("assertions", [])
            assertion_results = []
            if assertions:
                assertion_configs = [
                    {
                        "name": a.get("name", ""),
                        "type": a.get("type", ""),
                        "expression": a.get("expression", ""),
                        "operator": a.get("operator", "eq"),
                        "expected_value": a.get("expected_value", ""),
                    }
                    for a in assertions
                ]
                assertion_results = self.assertion_engine.assert_all(response, assertion_configs)

            # 5. 判断最终状态
            all_passed = all(r.passed for r in assertion_results) if assertion_results else True
            status = "passed" if all_passed else "failed"

            return ExecutionResult(
                status=status,
                request_url=url,
                request_method=method,
                request_headers=headers,
                request_body=body_content or "",
                response_status_code=response.status_code,
                response_headers=response.headers,
                response_body=response.body,
                duration_ms=response.duration_ms,
                assertion_results=[
                    {
                        "name": r.name,
                        "passed": r.passed,
                        "actual_value": r.actual_value,
                        "expected_value": r.expected_value,
                        "message": r.message,
                    }
                    for r in assertion_results
                ],
                extractor_results=extractor_results,
            )

        except Exception as e:
            return ExecutionResult(
                status="error",
                error_message=f"执行异常: {str(e)}",
            )

    def _build_url(self, base_url: str, path: str, var_engine: VariableEngine) -> str:
        """构建完整 URL"""
        # 替换路径中的变量
        rendered_path = var_engine.render(path)

        # 确保 base_url 不以 / 结尾
        base_url = base_url.rstrip("/")

        # 确保 path 以 / 开头
        if rendered_path and not rendered_path.startswith("/"):
            rendered_path = "/" + rendered_path

        return base_url + rendered_path
