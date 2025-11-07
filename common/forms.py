from django import forms
from .validators import ComplexityPasswordValidator

# 敏感词集合
SENSITIVE_WORDS = {"badword1", "badword2"}

def clean_sensitive(text: str) -> str:
    """对文本进行简单敏感词清洗（以 * 替换）。"""
    if not text:
        return text
    cleaned = text
    for w in SENSITIVE_WORDS:
        cleaned = cleaned.replace(w, "*")
    return cleaned

class BaseStyledForm(forms.Form):
    """基础表单：统一注入样式类（Bootstrap 兼容）。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()

class BaseModelForm(forms.ModelForm):
    """基础模型表单：统一样式与敏感词清洗。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        for k, v in list(cleaned.items()):
            if isinstance(v, str):
                cleaned[k] = clean_sensitive(v)
        return cleaned

class PasswordForm(BaseStyledForm):
    """单字段密码表单，带复杂度校验。"""
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        pwd = self.cleaned_data["password"]
        ComplexityPasswordValidator().validate(pwd)
        return pwd