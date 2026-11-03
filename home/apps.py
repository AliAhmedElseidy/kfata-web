from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    def ready(self):
        from . import signals  # noqa: F401
        from .smtp_forms import SMTPSettingsForm
        from .models import SMTPSettings
        SMTPSettings.base_form_class=SMTPSettingsForm
