from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from common.responses import json_success, json_error

@require_GET
def ping(request: HttpRequest):  # 健康检测端点
    return json_success({"pong": True})


def _attempt_keys(username, ip):  # 生成用户与 IP 级别的限制键
    return f"login:attempts:user:{username}", f"login:attempts:ip:{ip}"


@require_POST
def login_api(request: HttpRequest):  # 登录接口（支持用户名或 QQ），带双维度限流
    username = request.POST.get("username")
    password = request.POST.get("password")
    client_ip = request.META.get("REMOTE_ADDR", "0.0.0.0")

    if not username or not password:
        return json_error("缺少用户名或密码", status=400)

    user_key, ip_key = _attempt_keys(username, client_ip)
    user_attempts = cache.get(user_key, 0)
    ip_attempts = cache.get(ip_key, 0)

    if user_attempts >= settings.LOGIN_ATTEMPT_LIMIT or ip_attempts >= settings.LOGIN_ATTEMPT_LIMIT * 2:
        return json_error(f"登录失败过多，请 {settings.LOGIN_LOCKOUT_MINUTES} 分钟后再试", status=429)

    user = authenticate(request, username=username, password=password)
    if user is None:
        cache.set(user_key, user_attempts + 1, timeout=settings.LOGIN_LOCKOUT_MINUTES * 60)
        cache.set(ip_key, ip_attempts + 1, timeout=settings.LOGIN_LOCKOUT_MINUTES * 60)
        remaining = max(0, settings.LOGIN_ATTEMPT_LIMIT - (user_attempts + 1))
        return json_error(f"用户名或密码错误，剩余尝试次数：{remaining}", status=401)

    cache.delete(user_key)
    # 保留 IP 统计用于行为分析（可选：减少其计数）
    login(request, user)
    return json_success({"username": user.username, "id": user.id})

@require_GET
@cache_page(60)  # 缓存 60 秒示例端点，用于演示视图缓存
def cached_time(request: HttpRequest):
    import time
    return json_success({"ts": time.time()})
