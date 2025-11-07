from django.apps import AppConfig

class PlayersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "players"
    verbose_name = "玩家与权限"

    def ready(self):
        from . import signals  # noqa: F401

