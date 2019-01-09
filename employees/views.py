from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
from employees.forms import ProjectJoinForm
from employees.models import Report
from employees.serializers import ReportSerializer
from managers.models import Project


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
    reports_dict = {}
    project_form = ''
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return Report.objects.filter(author=self.request.user).order_by('-date', 'project__name')

    def _add_project(self, serializer, project):
        project.members.add(self.request.user)
        project.full_clean()
        project.save()
        serializer.fields['project'].initial = project

    def _create_serializer(self):
        reports_serializer = ReportSerializer(context={'request': self.request}, )
        reports_serializer.fields['project'].queryset = \
            Project.objects.filter(
                members__id=self.request.user.id
        ).order_by('name')
        return reports_serializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.reports_dict = query_as_dict(self.get_queryset())
        self.project_form = ProjectJoinForm(
            queryset=Project.objects.exclude(members__id=self.request.user.id).order_by('name'),
        )

    def get(self, _request):
        return Response({
            'serializer': self._create_serializer(),
            'reports_dict': self.reports_dict,
            'UI_text': ReportListStrings,
            'project_form': self.project_form,
        })

    def post(self, request):
        reports_serializer = ReportSerializer(data=request.data, context={'request': request})
        if 'join' in request.POST:
            project_id = request.POST['projects']
            project = Project.objects.get(id=int(project_id))
            self._add_project(serializer=reports_serializer, project=project)
            self.project_form = ProjectJoinForm(
                queryset=Project.objects.exclude(members__id=self.request.user.id).order_by('name'),
            )
            reports_serializer = self._create_serializer()
            reports_serializer.fields['project'].initial = project
            return Response({
                'serializer': reports_serializer,
                'reports_dict': self.reports_dict,
                'UI_text': ReportListStrings,
                'project_form': self.project_form,
            })

        elif not reports_serializer.is_valid():
            return Response({
                'serializer': reports_serializer,
                'reports_dict': self.reports_dict,
                'errors': reports_serializer.errors,
                'UI_text': ReportListStrings,
                'project_form': self.project_form,
            })
        reports_serializer.save(author=self.request.user)
        return Response({
            'serializer': self._create_serializer(),
            'reports_dict': query_as_dict(self.get_queryset()),
            'UI_text': ReportListStrings,
            'project_form': self.project_form,
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
