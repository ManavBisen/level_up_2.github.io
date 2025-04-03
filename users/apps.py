from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
        # Create default level titles when the app starts
        from users.signals import create_default_level_titles
        create_default_level_titles()
