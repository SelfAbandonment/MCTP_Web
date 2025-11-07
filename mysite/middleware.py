from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class SecurityHeadersMiddleware(MiddlewareMixin):
    """统一添加安全响应头，强化基础安全策略。"""
    def process_response(self, request, response: HttpResponse):
        # 安全相关响应头（防点击劫持 / 嗅探 / 引用策略 / 简单 XSS 提示 / 权限隔离）
        response.setdefault("X-Frame-Options", "DENY")  # 禁止被 iframe 嵌套
        response.setdefault("X-Content-Type-Options", "nosniff")  # 禁止浏览器猜测 MIME 类型
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")  # 引用策略
        response.setdefault("X-XSS-Protection", "1; mode=block")  # 旧版浏览器的 XSS 保护（现代浏览器已弃用）
        response.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")  # 限制敏感 API
        return response