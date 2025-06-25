from django.apps import AppConfig


class KitchatappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kitchatapp'
    def ready(self):
        import kitchatapp.signals
# apps.py

