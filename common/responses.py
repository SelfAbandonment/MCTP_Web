from django.http import JsonResponse

# 统一 JSON 响应封装（success/data/message 三段式）
def json_success(data=None, message="成功", status=200, **kwargs):
    payload = {"success": True, "data": data, "message": message}
    payload.update(kwargs)
    return JsonResponse(payload, status=status, safe=False)


def json_error(message="失败", data=None, status=400, **kwargs):
    payload = {"success": False, "data": data, "message": message}
    payload.update(kwargs)
    return JsonResponse(payload, status=status, safe=False)
