from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Action(ChoiceEnum):
    LIST = "list"
    RETRIEVE = "retrieve"
    CREATE = "create"
    UPDATE = "update"
