from django.apps import AppConfig


class FilmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'film'
    verbose_name = 'Models'

    def ready(self):
        import film.signals


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "users"
