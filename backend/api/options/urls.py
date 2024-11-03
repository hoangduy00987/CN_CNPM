from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'salary_ranges', AdminManageSalaryRangeMVS, basename='salary_range')
router.register(r'yoes', AdminManageYoeItemMVS, basename='yoe')
router.register(r'levels', AdminManageLevelItemMVS, basename='level')
router.register(r'skills', AdminManageSkillItemMVS, basename='skill')
router.register(r'job_types', AdminManageJobTypeMVS, basename='job_type')
router.register(r'contract_types', AdminManageContractTypeMVS, basename='contract_type')

urlpatterns = [
    path('get_all_salary_ranges/', SalaryRangeListView.as_view(), name='get_all_salary_ranges'),
    path('get_all_years_of_experience/', YoeListView.as_view(), name='get_all_years_of_experience'),
    path('get_all_levels/', LevelListView.as_view(), name='get_all_levels'),
    path('get_all_skills/', SkillListView.as_view(), name='get_all_skills'),
    path('get_all_job_types/', JobTypeListView.as_view(), name='get_all_job_types'),
    path('get_all_contract_types/', ContractTypeListView.as_view(), name='get_all_contract_types'),

    # Admin
    path('', include(router.urls)),
]
