from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UsernameOrQQBackend(ModelBackend):
    """支持通过用户名或 QQ 号进行身份认证的后端。"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username_field = getattr(User, 'USERNAME_FIELD', 'username')
            username = kwargs.get(username_field)
        if username is None or password is None:
            return None

        # 仅查询首条匹配记录，不会抛出异常
        user = (
            User.objects
            .filter(Q(username=username) | Q(qq=username))
            .first()
        )
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
