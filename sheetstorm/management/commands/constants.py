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


class UsersInProjects(Enum):
    EMPLOYEE_SUSPENDED = "employee_suspended"
    EMPLOYEE_ACTIVE = "employee_active"
    EMPLOYEE_COMPLETED = "employee_completed"
    MANAGER_SUSPENDED = "manager_suspended"
    MANAGER_ACTIVE = "manager_active"
    MANAGER_COMPLETED = "manager_completed"
    ADMIN_SUSPENDED = "admin_suspended"
    ADMIN_ACTIVE = "admin_active"
    ADMIN_COMPLETED = "admin_completed"


SMALL_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 2,
    CustomUser.UserType.EMPLOYEE.name: 15,
    CustomUser.UserType.MANAGER.name: 3,
    ProjectType.SUSPENDED.name: 1,
    ProjectType.ACTIVE.name: 5,
    ProjectType.COMPLETED.name: 3,
    UsersInProjects.EMPLOYEE_SUSPENDED.name: 5,
    UsersInProjects.EMPLOYEE_ACTIVE.name: 10,
    UsersInProjects.EMPLOYEE_COMPLETED.name: 5,
    UsersInProjects.MANAGER_SUSPENDED.name: 2,
    UsersInProjects.MANAGER_ACTIVE.name: 2,
    UsersInProjects.MANAGER_COMPLETED.name: 2,
    UsersInProjects.ADMIN_SUSPENDED.name: 2,
    UsersInProjects.ADMIN_ACTIVE.name: 2,
    UsersInProjects.ADMIN_COMPLETED.name: 2,
}

MEDIUM_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 20,
    CustomUser.UserType.EMPLOYEE.name: 150,
    CustomUser.UserType.MANAGER.name: 30,
    ProjectType.SUSPENDED.name: 5,
    ProjectType.ACTIVE.name: 25,
    ProjectType.COMPLETED.name: 15,
    UsersInProjects.EMPLOYEE_SUSPENDED.name: 50,
    UsersInProjects.EMPLOYEE_ACTIVE.name: 80,
    UsersInProjects.EMPLOYEE_COMPLETED.name: 50,
    UsersInProjects.MANAGER_SUSPENDED.name: 15,
    UsersInProjects.MANAGER_ACTIVE.name: 15,
    UsersInProjects.MANAGER_COMPLETED.name: 15,
    UsersInProjects.ADMIN_SUSPENDED.name: 20,
    UsersInProjects.ADMIN_ACTIVE.name: 20,
    UsersInProjects.ADMIN_COMPLETED.name: 20,
}

LARGE_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 90,
    CustomUser.UserType.EMPLOYEE.name: 350,
    CustomUser.UserType.MANAGER.name: 120,
    ProjectType.SUSPENDED.name: 20,
    ProjectType.ACTIVE.name: 60,
    ProjectType.COMPLETED.name: 30,
    UsersInProjects.EMPLOYEE_SUSPENDED.name: 130,
    UsersInProjects.EMPLOYEE_ACTIVE.name: 200,
    UsersInProjects.EMPLOYEE_COMPLETED.name: 100,
    UsersInProjects.MANAGER_SUSPENDED.name: 50,
    UsersInProjects.MANAGER_ACTIVE.name: 50,
    UsersInProjects.MANAGER_COMPLETED.name: 50,
    UsersInProjects.ADMIN_SUSPENDED.name: 70,
    UsersInProjects.ADMIN_ACTIVE.name: 70,
    UsersInProjects.ADMIN_COMPLETED.name: 70,
}

EXTRA_LARGE_SET = {
    SUPERUSER_USER_TYPE: True,
    CustomUser.UserType.ADMIN.name: 120,
    CustomUser.UserType.EMPLOYEE.name: 600,
    CustomUser.UserType.MANAGER.name: 200,
    ProjectType.SUSPENDED.name: 30,
    ProjectType.ACTIVE.name: 90,
    ProjectType.COMPLETED.name: 60,
    UsersInProjects.EMPLOYEE_SUSPENDED.name: 200,
    UsersInProjects.EMPLOYEE_ACTIVE.name: 400,
    UsersInProjects.EMPLOYEE_COMPLETED.name: 200,
    UsersInProjects.MANAGER_SUSPENDED.name: 80,
    UsersInProjects.MANAGER_ACTIVE.name: 80,
    UsersInProjects.MANAGER_COMPLETED.name: 80,
    UsersInProjects.ADMIN_SUSPENDED.name: 100,
    UsersInProjects.ADMIN_ACTIVE.name: 100,
    UsersInProjects.ADMIN_COMPLETED.name: 100,
}

DATA_SETS = {
    DataSize.SMALL.value: SMALL_SET,
    DataSize.MEDIUM.value: MEDIUM_SET,
    DataSize.LARGE.value: LARGE_SET,
    DataSize.EXTRA_LARGE.value: EXTRA_LARGE_SET,
}
