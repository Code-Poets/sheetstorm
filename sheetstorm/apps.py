from django.apps import AppConfig


class SheetstormConfig(AppConfig):
    name = "sheetstorm"

    def ready(self) -> None:
        from sheetstorm import system_check  # noqa, flake8 F401 issue  # pylint: disable=unused-import
