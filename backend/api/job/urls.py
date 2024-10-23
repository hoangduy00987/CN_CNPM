from django.urls import path
from .views import *

get_application_infor = ApplicationInforMVS.as_view({
    'get': 'get_application_infor'
})
get_list_application_candidate = ApplicationInforMVS.as_view({
    'get': 'get_list_application_candidate'
})
get_list_candidate_applied_for_job = ApplicationInforMVS.as_view({
    'get': 'get_list_candidate_applied_for_job'
})

urlpatterns = [
    path('search/', JobSearchView.as_view(), name='job_search'),
    path('post-recruitment/', JobPostView.as_view(), name='post_recruitment'),
    path('update-recruitment/', JobUpdateView.as_view(), name='update_recruitment'),
    path('job-list-of-company/', JobListOfCompanyView.as_view(), name='job_list_company'),
    path('get-all-job-categories/', JobCategoryListView.as_view(), name='get_all_job_categories'),
    path('hide-recruitment/', HideJobView.as_view(), name='hide_job'),
    path('apply/', JobApplicationView.as_view(), name='job_application'),
    path('get_application_infor/', get_application_infor),
    path('get_list_application_candidate/', get_list_application_candidate),
    path('get_list_candidate_applied_for_job/', get_list_candidate_applied_for_job),
    path('approve_application/', ApproveApplicationView.as_view(), name='approve_application'),
    path('follow/', FollowJobView.as_view(), name='follow_job'),
]