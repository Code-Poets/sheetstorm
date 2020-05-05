from django.apps import AppConfig


class SheetstormConfig(AppConfig):
    name = "sheetstorm"

    def ready(self) -> None:
        from sheetstorm import system_check  # noqa: F401  # pylint: disable=unused-import, import-outside-toplevel
