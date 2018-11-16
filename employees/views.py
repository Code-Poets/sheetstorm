from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
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


def query_as_dict(query_set):
    dictionary = {}
    for record in query_set:
        key = record.date
        dictionary.setdefault(key, [])
        dictionary[key].append(record)
    return dictionary


class ReportList(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'employees/report_list.html'
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return Report.objects.filter(author=self.request.user).order_by('-date', 'project__name')

    def get(self, request):
        reports_serializer = ReportSerializer(context={'request': request})
        reports_dict = query_as_dict(self.get_queryset())
        return Response({
            'serializer': reports_serializer,
            'reports_dict': reports_dict,
            'UI_text': ReportListStrings,
        })

    def post(self, request):
        reports_serializer = ReportSerializer(data=request.data, context={'request': request})
        if not reports_serializer.is_valid():
            return Response({
                'serializer': reports_serializer,
                'reports_dict': query_as_dict(self.get_queryset()),
                'errors': reports_serializer.errors,
                'UI_text': ReportListStrings,
            })
        reports_serializer.save(author=self.request.user)
        reports_serializer = ReportSerializer(context={'request': request})
        return Response({
            'serializer': reports_serializer,
            'reports_dict': query_as_dict(self.get_queryset()),
            'UI_text': ReportListStrings,
        }, status=201)


class ReportDetail(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'employees/report_detail.html'
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        serializer = ReportSerializer(report, context={'request': request})
        return Response({
            'serializer': serializer,
            'report': report,
            'UI_text': ReportDetailStrings,
        })

    def post(self, request, pk):
        if "discard" not in request.POST:
            report = get_object_or_404(Report, pk=pk)
            serializer = ReportSerializer(
                report,
                data=request.data,
                context={'request': request}
            )
            if not serializer.is_valid():
                return Response({
                    'serializer': serializer,
                    'report': report,
                    'errors': serializer.errors,
                    'UI_text': ReportDetailStrings,
                })
            serializer.save()
        return redirect('custom-report-list')


def delete_report(_request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.delete()
    return redirect('custom-report-list')
