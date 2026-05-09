from django.apps import AppConfig
from django.utils.module_loading import import_module


class NewsPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'News_Portal'

    def ready(self):
        import_module('News_Portal.signals')