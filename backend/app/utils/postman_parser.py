"""
Postman Collection v2.1 解析器

支持：
- 嵌套文件夹 → 模块
- 请求 → 用例
- Collection 变量 → 环境变量
"""

import json
from typing import Any
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode


@dataclass
class ParsedRequest:
    """解析后的请求"""
    name: str
    description: str = ""
    method: str = "GET"
    path: str = "/"
    headers: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    body_type: str = "none"
    body_content: str = ""
    folder_path: list = field(default_factory=list)  # 所属文件夹路径


@dataclass
class ParsedFolder:
    """解析后的文件夹（模块）"""
    name: str
    description: str = ""
    parent_path: list = field(default_factory=list)  # 父级路径


@dataclass
class ParsedVariable:
    """解析后的变量"""
    key: str
    value: str
    type: str = "default"


@dataclass
class ParseResult:
    """解析结果"""
    collection_name: str
    collection_description: str = ""
    requests: list = field(default_factory=list)
    folders: list = field(default_factory=list)
    variables: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class PostmanParser:
    """Postman Collection v2.1 解析器"""

    SUPPORTED_SCHEMA = "https://schema.getpostman.com/json/collection/v2"

    def __init__(self):
        self.result = None

    def parse(self, content: str | dict) -> ParseResult:
        """
        解析 Postman Collection

        Args:
            content: JSON 字符串或已解析的字典

        Returns:
            ParseResult: 解析结果
        """
        # 解析 JSON
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                return ParseResult(
                    collection_name="",
                    errors=[f"JSON 解析失败: {str(e)}"]
                )
        else:
            data = content

        # 验证格式
        if not self._validate_schema(data):
            return ParseResult(
                collection_name="",
                errors=["不支持的 Postman Collection 格式，请使用 v2.1 格式导出"]
            )

        # 提取基本信息
        info = data.get("info", {})
        collection_name = info.get("name", "Imported Collection")
        collection_description = info.get("description", "")

        self.result = ParseResult(
            collection_name=collection_name,
            collection_description=collection_description,
        )

        # 解析变量
        self._parse_variables(data.get("variable", []))

        # 解析 items（文件夹和请求）
        self._parse_items(data.get("item", []), folder_path=[])

        return self.result

    def _validate_schema(self, data: dict) -> bool:
        """验证是否为支持的 Postman Collection 格式"""
        info = data.get("info", {})
        schema = info.get("schema", "")
        return schema.startswith(self.SUPPORTED_SCHEMA)

    def _parse_variables(self, variables: list):
        """解析 Collection 变量"""
        for var in variables:
            if isinstance(var, dict):
                self.result.variables.append(ParsedVariable(
                    key=var.get("key", ""),
                    value=var.get("value", ""),
                    type=var.get("type", "default"),
                ))

    def _parse_items(self, items: list, folder_path: list):
        """
        递归解析 items

        Args:
            items: item 列表
            folder_path: 当前文件夹路径
        """
        for item in items:
            if not isinstance(item, dict):
                continue

            # 判断是文件夹还是请求
            if "item" in item:
                # 是文件夹
                self._parse_folder(item, folder_path)
            elif "request" in item:
                # 是请求
                self._parse_request(item, folder_path)

    def _parse_folder(self, item: dict, parent_path: list):
        """解析文件夹"""
        name = item.get("name", "Unnamed Folder")
        description = ""

        # 描述可能是字符串或对象
        desc = item.get("description")
        if isinstance(desc, str):
            description = desc
        elif isinstance(desc, dict):
            description = desc.get("content", "")

        # 添加到结果
        self.result.folders.append(ParsedFolder(
            name=name,
            description=description,
            parent_path=parent_path.copy(),
        ))

        # 递归解析子项
        current_path = parent_path + [name]
        self._parse_items(item.get("item", []), current_path)

    def _parse_request(self, item: dict, folder_path: list):
        """解析请求"""
        try:
            name = item.get("name", "Unnamed Request")

            # 描述
            description = ""
            desc = item.get("description")
            if isinstance(desc, str):
                description = desc
            elif isinstance(desc, dict):
                description = desc.get("content", "")

            request = item.get("request", {})

            # 如果 request 是字符串（简化格式），转换为字典
            if isinstance(request, str):
                request = {"url": request, "method": "GET"}

            # 方法
            method = request.get("method", "GET").upper()

            # URL 解析
            url_data = request.get("url", "")
            path, params = self._parse_url(url_data)

            # Headers
            headers = self._parse_headers(request.get("header", []))

            # Body
            body_type, body_content = self._parse_body(request.get("body"))

            self.result.requests.append(ParsedRequest(
                name=name,
                description=description,
                method=method,
                path=path,
                headers=headers,
                params=params,
                body_type=body_type,
                body_content=body_content,
                folder_path=folder_path.copy(),
            ))

        except Exception as e:
            self.result.errors.append(f"解析请求 '{item.get('name', 'unknown')}' 失败: {str(e)}")

    def _parse_url(self, url_data: Any) -> tuple[str, dict]:
        """
        解析 URL

        Args:
            url_data: URL 数据（可能是字符串或对象）

        Returns:
            (path, params)
        """
        params = {}

        if isinstance(url_data, str):
            # 简单字符串格式
            parsed = urlparse(url_data)
            path = parsed.path or "/"
            if parsed.query:
                params = {k: v[0] if len(v) == 1 else v
                          for k, v in parse_qs(parsed.query).items()}
            return path, params

        if isinstance(url_data, dict):
            # 对象格式
            # 解析 path
            path_parts = url_data.get("path", [])
            if isinstance(path_parts, list):
                path = "/" + "/".join(str(p) for p in path_parts)
            else:
                path = str(path_parts)

            # 解析 query 参数
            query = url_data.get("query", [])
            for q in query:
                if isinstance(q, dict) and not q.get("disabled", False):
                    key = q.get("key", "")
                    value = q.get("value", "")
                    if key:
                        params[key] = value

            return path, params

        return "/", {}

    def _parse_headers(self, headers: list) -> dict:
        """解析请求头"""
        result = {}
        for h in headers:
            if isinstance(h, dict) and not h.get("disabled", False):
                key = h.get("key", "")
                value = h.get("value", "")
                if key:
                    result[key] = value
        return result

    def _parse_body(self, body: dict | None) -> tuple[str, str]:
        """
        解析请求体

        Returns:
            (body_type, body_content)
        """
        if not body:
            return "none", ""

        mode = body.get("mode", "")

        if mode == "raw":
            content = body.get("raw", "")
            # 检查是否有语言选项
            options = body.get("options", {})
            raw_options = options.get("raw", {})
            language = raw_options.get("language", "text")

            if language == "json":
                return "json", content
            elif language == "xml":
                return "xml", content
            else:
                return "raw", content

        elif mode == "formdata":
            form_data = body.get("formdata", [])
            data = {}
            for item in form_data:
                if isinstance(item, dict) and not item.get("disabled", False):
                    key = item.get("key", "")
                    value = item.get("value", "")
                    if key:
                        data[key] = value
            return "form-data", json.dumps(data, ensure_ascii=False)

        elif mode == "urlencoded":
            urlencoded = body.get("urlencoded", [])
            data = {}
            for item in urlencoded:
                if isinstance(item, dict) and not item.get("disabled", False):
                    key = item.get("key", "")
                    value = item.get("value", "")
                    if key:
                        data[key] = value
            return "x-www-form-urlencoded", json.dumps(data, ensure_ascii=False)

        elif mode == "file":
            return "binary", ""

        elif mode == "graphql":
            graphql = body.get("graphql", {})
            return "graphql", json.dumps(graphql, ensure_ascii=False)

        return "none", ""


def parse_postman_collection(content: str | dict) -> ParseResult:
    """
    解析 Postman Collection 的便捷函数

    Args:
        content: JSON 字符串或字典

    Returns:
        ParseResult: 解析结果
    """
    parser = PostmanParser()
    return parser.parse(content)
