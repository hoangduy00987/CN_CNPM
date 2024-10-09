import django_filters
from ..submodels.models_recruitment import Job

class JobFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    salary_range = django_filters.CharFilter(field_name='salary_range', lookup_expr='icontains')
    skill_required = django_filters.CharFilter(field_name='skill_required', lookup_expr='icontains')

    class Meta:
        model = Job
        fields = ['location', 'salary_range', 'skill_required']
