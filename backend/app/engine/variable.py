import re
import json


class VariableEngine:
    """变量替换引擎，支持 {{variable}} 语法"""

    PATTERN = re.compile(r'\{\{(\w+)\}\}')

    def __init__(self, env_vars: dict = None, extracted_vars: dict = None, global_vars: dict = None):
        """
        初始化变量上下文
        优先级：extracted_vars > env_vars > global_vars
        """
        self.context = {}
        if global_vars:
            self.context.update(global_vars)
        if env_vars:
            self.context.update(env_vars)
        if extracted_vars:
            self.context.update(extracted_vars)

    def update(self, variables: dict):
        """更新变量上下文"""
        self.context.update(variables)

    def render(self, text: str) -> str:
        """将 {{var}} 替换为实际值"""
        if not text:
            return text

        def replacer(match):
            key = match.group(1)
            value = self.context.get(key)
            if value is not None:
                return str(value)
            return match.group(0)  # 保留原样

        return self.PATTERN.sub(replacer, text)

    def render_dict(self, data: dict) -> dict:
        """递归替换字典中的变量"""
        if not data:
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.render(value)
            elif isinstance(value, dict):
                result[key] = self.render_dict(value)
            elif isinstance(value, list):
                result[key] = self.render_list(value)
            else:
                result[key] = value
        return result

    def render_list(self, data: list) -> list:
        """递归替换列表中的变量"""
        if not data:
            return data

        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.render(item))
            elif isinstance(item, dict):
                result.append(self.render_dict(item))
            elif isinstance(item, list):
                result.append(self.render_list(item))
            else:
                result.append(item)
        return result

    def render_json(self, json_str: str) -> str:
        """替换 JSON 字符串中的变量"""
        if not json_str:
            return json_str

        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                rendered = self.render_dict(data)
            elif isinstance(data, list):
                rendered = self.render_list(data)
            else:
                return self.render(json_str)
            return json.dumps(rendered, ensure_ascii=False)
        except json.JSONDecodeError:
            # 不是有效 JSON，直接替换字符串
            return self.render(json_str)
