from django.apps import AppConfig


class OdontoproConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'odontoPro'

    def ready(self):
        import odontoPro.signals  # noqa: F401
