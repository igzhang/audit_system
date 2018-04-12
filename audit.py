import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audit.settings")
    import django
    django.setup()
    from src import user_interactive
    obj = user_interactive.UserShell()
    obj.start()