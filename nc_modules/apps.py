from django.apps import AppConfig
from django.db import connection
from django.db.models.signals import post_migrate

data = [
    {
        "name": "archive",
        "verbose_name": "Архив",
        "type": "global"
    },
    {
        "name": "basket",
        "verbose_name": "Корзина",
        "type": "global"
    },
    {
        "name": "clients",
        "verbose_name": "Клиенты",
        "type": "global"
    },
    {
        "name": "members",
        "verbose_name": "Участники",
        "type": "global"
    },
    {
        "name": "reports",
        "verbose_name": "Отчеты",
        "type": "global"
    },
]


def post_migrate_modules(sender: AppConfig, **kwargs):
    if sender.name + "_module" in connection.introspection.table_names():
        Module = sender.get_model('Module')
        for kw in data:
            if not Module.objects.filter(name=kw["name"]).exists():
                Module.objects.create(**kw)


class NcModulesConfig(AppConfig):
    name = 'nc_modules'
    verbose_name = 'Nc Modules'

    def ready(self):
        post_migrate.connect(post_migrate_modules, sender=self)
