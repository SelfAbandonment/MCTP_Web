from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class SecurityHeadersMiddleware(MiddlewareMixin):
    """统一添加安全响应头，强化基础安全策略。"""
    def __init__(self, get_response):
        super().__init__(get_response)
        # 实例级配置，便于后续扩展与测试
        self._policies = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-XSS-Protection": "1; mode=block",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

    def process_response(self, request, response: HttpResponse):
        # 显式使用 request 以满足静态检查；未来可按路径/方法定制策略
        _ = (request.method, request.path)
        for header, value in self._policies.items():
            response.setdefault(header, value)
        return response