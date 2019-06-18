from django.db.models import Q
from django.db.models import QuerySet


class NotCallableMixin:
    do_not_call_in_templates = True


class UserIsManagerOfCurrentProjectMixin:
    def get_queryset(self) -> QuerySet:
        if self.request.user.is_manager:  # type: ignore
            return super().get_queryset().filter(managers=self.request.user.pk)  # type: ignore
        else:
            return super().get_queryset()  # type: ignore


class UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin:
    def get_queryset(self) -> QuerySet:
        if self.request.user.is_manager:  # type: ignore
            return (
                super()  # type: ignore
                .get_queryset()
                .filter(Q(project__managers=self.request.user.pk) | Q(author=self.request.user.pk))  # type: ignore
            )
        else:
            return super().get_queryset()  # type: ignore


class UserIsAuthorOfCurrentReportMixin:
    def get_queryset(self) -> QuerySet:
        if self.request.user.is_employee:  # type: ignore
            return super().get_queryset().filter(author=self.request.user.pk)  # type: ignore
        else:
            return super().get_queryset()  # type: ignore
