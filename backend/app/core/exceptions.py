class ApiException(Exception):
    def __init__(self, code: int, message: str, detail: str | None = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundError(ApiException):
    def __init__(self, message: str = "资源不存在", detail: str | None = None):
        super().__init__(code=40400, message=message, detail=detail)


class ValidationError(ApiException):
    def __init__(self, message: str = "参数错误", detail: str | None = None):
        super().__init__(code=40001, message=message, detail=detail)


class DuplicateError(ApiException):
    def __init__(self, message: str = "资源已存在", detail: str | None = None):
        super().__init__(code=40002, message=message, detail=detail)


class ExecutionError(ApiException):
    def __init__(self, message: str = "执行失败", detail: str | None = None):
        super().__init__(code=50001, message=message, detail=detail)
