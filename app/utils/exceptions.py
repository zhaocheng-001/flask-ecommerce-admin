# -*- coding: utf-8 -*-
"""自定义业务异常，由全局错误处理器统一捕获后返回"""


class ApiError(Exception):
    """业务异常：抛出后由 @app.errorhandler(ApiError) 统一处理"""

    def __init__(self, message="业务异常", code=1):
        super().__init__(message)
        self.message = message
        self.code = code
