from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

TAGS = [
    {
        "title": "Красный",
        "color": "FD6461"
    },
    {
        "title": "Оранжевый",
        "color": "F7A650"
    },
    {
        "title": "Желтый",
        "color": "F4CD56"
    },
    {
        "title": "Зеленый",
        "color": "71CA58"
    },
    {
        "title": "Лиловый",
        "color": "D08CE0"
    }
]


def post_migrate_tags(sender: AppConfig, **kwargs):
    Tag = sender.get_model("Tag")
    for data in TAGS:
        if not Tag.objects.filter(color=data['color']).exists():
            Tag.objects.create(**data)


class NcClientsConfig(AppConfig):
    name = 'nc_clients'
    verbose_name = _("Clients")

    def ready(self):
        post_migrate.connect(post_migrate_tags, sender=self)
