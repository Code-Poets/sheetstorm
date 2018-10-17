from rest_framework import permissions
from rest_framework import viewsets

from employees.models import Report
from employees.serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        )

    def get_queryset(self):
        return Report.objects.filter(author=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
