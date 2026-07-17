class NotFoundException(Exception):
    def __init__(self, message="资源不存在"):
        self.message = message
        super().__init__(message)


class ConflictException(Exception):
    def __init__(self, message="资源冲突"):
        self.message = message
        super().__init__(message)


class ValidationException(Exception):
    def __init__(self, message="参数校验失败"):
        self.message = message
        super().__init__(message)
