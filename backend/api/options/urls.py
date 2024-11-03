from django.urls import path
from .views import *

urlpatterns = [
    path('get_all_salary_ranges/', SalaryRangeListView.as_view(), name='get_all_salary_ranges'),
    path('get_all_years_of_experience/', YoeListView.as_view(), name='get_all_years_of_experience'),
    path('get_all_levels/', LevelListView.as_view(), name='get_all_levels'),
    path('get_all_skills/', SkillListView.as_view(), name='get_all_skills'),
    path('get_all_job_types/', JobTypeListView.as_view(), name='get_all_job_types'),
    path('get_all_contract_types/', ContractTypeListView.as_view(), name='get_all_contract_types'),
]
