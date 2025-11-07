import re
from django.core.exceptions import ValidationError

class ComplexityPasswordValidator:
    """密码复杂度校验器：可配置大写/小写/数字/符号的最小数量."""
    def __init__(self, min_upper=1, min_lower=1, min_digits=1, min_symbols=1):
        self.min_upper = min_upper
        self.min_lower = min_lower
        self.min_digits = min_digits
        self.min_symbols = min_symbols
        self.symbol_pattern = re.compile(r"[!@#$%^&*()_+\-={}[\\]|:;\"'<>,.?/]")

    def validate(self, password, user=None):
        """校验密码是否满足复杂度要求."""
        _ = user  # 参数保留以兼容 Django 密码校验器接口
        upper = sum(1 for c in password if c.isupper())
        lower = sum(1 for c in password if c.islower())
        digits = sum(1 for c in password if c.isdigit())
        symbols = len(self.symbol_pattern.findall(password))
        if upper < self.min_upper or lower < self.min_lower or digits < self.min_digits or symbols < self.min_symbols:
            raise ValidationError(
                f"密码复杂度不足: 至少{self.min_upper}大写,{self.min_lower}小写,{self.min_digits}数字,{self.min_symbols}符号",
                code="password_complexity",
            )

    def get_help_text(self):
        return f"密码至少包含{self.min_upper}个大写字母、{self.min_lower}个小写字母、{self.min_digits}个数字和{self.min_symbols}个符号"
