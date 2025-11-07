"""
mysite 项目 URL 路由配置。
此处统一挂载后台、富文本上传、API 等入口；开发环境追加调试工具与静态/媒体文件服务。
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include,path
from debug_toolbar.toolbar import debug_toolbar_urls
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),  # 后台管理
    path('ckeditor/', include('ckeditor_uploader.urls')),  # CKEditor 上传
    path('api/', include('api.urls')),  # API 路由
    path('', lambda r: JsonResponse({"success": True, "data": None, "message": "MCTP API"})),  # 根入口
]
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar_urls()))]  # 调试工具栏
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 媒体文件
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # 静态文件
