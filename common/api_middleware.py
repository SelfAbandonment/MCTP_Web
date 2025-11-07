import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class ApiExceptionMiddleware(MiddlewareMixin):
    """统一拦截 API 异常，返回规范化 JSON 响应。"""
    def process_exception(self, request, exception):
        # 若为 API 请求或客户端期望 JSON，则返回统一错误格式
        wants_json = request.path.startswith('/api/') or request.headers.get('accept') == 'application/json'
        if wants_json:
            logger.exception("API 异常: %s", exception)
            return JsonResponse({"success": False, "data": None, "message": str(exception)}, status=500)
        return None