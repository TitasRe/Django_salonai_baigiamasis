from django.apps import AppConfig


class SalonoRezervacijosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'salono_rezervacijos'

    def ready(self):
        from .signals import create_profile