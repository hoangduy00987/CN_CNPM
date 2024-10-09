from django.urls import path
from .views import *

urlpatterns = [
    path('search/', JobSearchView.as_view(), name='job_search'),
    path('post-recruitment/', JobPostView.as_view(), name='post_recruitment'),
    path('update-recruitment/', JobUpdateView.as_view(), name='update_recruitment'),
    path('job-list-of-company/', JobListOfCompanyView.as_view(), name='job_list_company'),
    path('get-all-job-categories/', JobCategoryListView.as_view(), name='get_all_job_categories'),
    path('hide-recruitment/', HideJobView.as_view(), name='hide_job'),
    path('apply/', JobApplicationView.as_view(), name='job_application'),
]