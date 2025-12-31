import time
import json
from dataclasses import dataclass

import httpx


@dataclass
class HttpResponse:
    """HTTP 响应对象"""
    status_code: int
    headers: dict
    body: str
    cookies: dict
    duration_ms: int
    error: str = None

    @property
    def json(self):
        """解析 JSON 响应"""
        try:
            return json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return None


class HttpClient:
    """异步 HTTP 客户端"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        params: dict = None,
        body_type: str = "none",
        body_content: str = None,
    ) -> HttpResponse:
        """
        发送 HTTP 请求

        Args:
            method: 请求方法 (GET/POST/PUT/DELETE/PATCH)
            url: 请求 URL
            headers: 请求头
            params: Query 参数
            body_type: Body 类型 (none/json/form/form-data/raw)
            body_content: Body 内容

        Returns:
            HttpResponse 对象
        """
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 构建请求参数
                request_kwargs = {
                    "method": method.upper(),
                    "url": url,
                    "headers": headers or {},
                    "params": params or {},
                }

                # 处理不同的 Body 类型
                if body_type == "json" and body_content:
                    request_kwargs["content"] = body_content
                    if "Content-Type" not in request_kwargs["headers"]:
                        request_kwargs["headers"]["Content-Type"] = "application/json"

                elif body_type == "form" and body_content:
                    # URL 编码的表单数据
                    try:
                        form_data = json.loads(body_content)
                        request_kwargs["data"] = form_data
                    except json.JSONDecodeError:
                        request_kwargs["content"] = body_content

                elif body_type == "form-data" and body_content:
                    # multipart/form-data
                    try:
                        form_data = json.loads(body_content)
                        request_kwargs["files"] = {
                            k: (None, str(v)) for k, v in form_data.items()
                        }
                    except json.JSONDecodeError:
                        request_kwargs["content"] = body_content

                elif body_type == "raw" and body_content:
                    request_kwargs["content"] = body_content

                # 发送请求
                response = await client.request(**request_kwargs)

                duration_ms = int((time.time() - start_time) * 1000)

                return HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.text,
                    cookies=dict(response.cookies),
                    duration_ms=duration_ms,
                )

        except httpx.TimeoutException:
            duration_ms = int((time.time() - start_time) * 1000)
            return HttpResponse(
                status_code=0,
                headers={},
                body="",
                cookies={},
                duration_ms=duration_ms,
                error=f"请求超时 (>{self.timeout}s)",
            )

        except httpx.RequestError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return HttpResponse(
                status_code=0,
                headers={},
                body="",
                cookies={},
                duration_ms=duration_ms,
                error=f"请求失败: {str(e)}",
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return HttpResponse(
                status_code=0,
                headers={},
                body="",
                cookies={},
                duration_ms=duration_ms,
                error=f"未知错误: {str(e)}",
            )
