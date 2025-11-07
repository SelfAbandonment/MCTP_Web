from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test


def json_forbidden(message="无权限"):
    """以统一 JSON 结构返回 403。"""
    return JsonResponse({"success": False, "data": None, "message": message}, status=403)


def admin_required(view_func=None):
    """管理员权限校验装饰器."""
    def check(user):
        return user.is_authenticated and user.is_staff

    decorator = user_passes_test(check, login_url=None)

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not check(request.user):
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.headers.get("accept") == "application/json":
                return json_forbidden("管理员权限不足")
            return HttpResponseForbidden("管理员权限不足")
        return view_func(request, *args, **kwargs)

    return decorator if view_func is None else _wrapped_view


essential_player_check = lambda u: u.is_authenticated and getattr(u, "is_active", False)

def player_required(view_func=None):
    """玩家权限校验装饰器（需已登录且账号有效）。"""
    decorator = user_passes_test(essential_player_check, login_url=None)

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not essential_player_check(request.user):
            if request.headers.get("accept") == "application/json":
                return json_forbidden("玩家权限不足")
            return HttpResponseForbidden("玩家权限不足")
        return view_func(request, *args, **kwargs)

    return decorator if view_func is None else _wrapped_view
