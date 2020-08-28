from enum import Enum

from users.models import CustomUser

SUPERUSER_USER_TYPE = "SUPERUSER"

DATA_SIZE_PARAMETER = "data_size"


class DataSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


class ProjectType(Enum):
    SUSPENDED = "suspended"
    ACTIVE = "active"
    COMPLETED = "completed"


SMALL_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 2,
    CustomUser.UserType.EMPLOYEE.name: 15,
    CustomUser.UserType.MANAGER.name: 3,
    ProjectType.SUSPENDED.name: 1,
    ProjectType.ACTIVE.name: 5,
    ProjectType.COMPLETED.name: 2,
}

MEDIUM_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 10,
    CustomUser.UserType.EMPLOYEE.name: 70,
    CustomUser.UserType.MANAGER.name: 20,
    ProjectType.SUSPENDED.name: 7,
    ProjectType.ACTIVE.name: 25,
    ProjectType.COMPLETED.name: 10,
}

LARGE_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 70,
    CustomUser.UserType.EMPLOYEE.name: 300,
    CustomUser.UserType.MANAGER.name: 100,
    ProjectType.SUSPENDED.name: 50,
    ProjectType.ACTIVE.name: 150,
    ProjectType.COMPLETED.name: 70,
}

EXTRA_LARGE_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 250,
    CustomUser.UserType.EMPLOYEE.name: 1000,
    CustomUser.UserType.MANAGER.name: 400,
    ProjectType.SUSPENDED.name: 150,
    ProjectType.ACTIVE.name: 450,
    ProjectType.COMPLETED.name: 250,
}

DATA_SETS = {
    DataSize.SMALL.value: SMALL_SET,
    DataSize.MEDIUM.value: MEDIUM_SET,
    DataSize.LARGE.value: LARGE_SET,
    DataSize.EXTRA_LARGE.value: EXTRA_LARGE_SET,
}
