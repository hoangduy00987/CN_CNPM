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
check_candidate_applied_job = ApplicationInforMVS.as_view({
    'get': 'check_candidate_applied_job'
})
get_job_posting_limit = JobPostingLimitOfCompanyMVS.as_view({
    'get': 'get_job_posting_limit'
})

# ========== Admin ============
admin_accept_job_posting = AdminManageJobPostingMVS.as_view({
    'post': 'admin_accept_job_posting'
})
admin_reject_job_posting = AdminManageJobPostingMVS.as_view({
    'post': 'admin_reject_job_posting'
})

urlpatterns = [
    path('search/', JobSearchView.as_view(), name='job_search'),
    path('post-recruitment/', JobPostView.as_view(), name='post_recruitment'),
    path('update-recruitment/', JobUpdateView.as_view(), name='update_recruitment'),
    path('job-list-of-company/', JobListOfCompanyView.as_view(), name='job_list_company'),
    path('get-all-job-categories/', JobCategoryListView.as_view(), name='get_all_job_categories'),
    path('detail-job/', JobDetailView.as_view(), name='detail_job'),
    path('hide-recruitment/', HideJobView.as_view(), name='hide_job'),
    path('apply/', JobApplicationView.as_view(), name='job_application'),
    path('get_application_infor/', get_application_infor, name='get_application_infor'),
    path('get_list_application_candidate/', get_list_application_candidate, name='get_list_application_candidate'),
    path('get_list_candidate_applied_for_job/', get_list_candidate_applied_for_job, name='get_list_candidate_applied_for_job'),
    path('check_candidate_applied_job/', check_candidate_applied_job, name='check_candidate_applied_job'),
    path('approve_application/', ApproveApplicationView.as_view(), name='approve_application'),
    path('notifications_job/', NotificationListView.as_view(), name='notification-list'),
    path('follow/', FollowJobView.as_view(), name='follow_job'),
    path('user-get-list-follow-job/', ListJobFollowOfUserView.as_view(), name='user_get_list_follow_job'),
    path('add-interview-information/', AddInterviewInformationView.as_view(), name='add_interview_infor'),
    path('get_job_posting_limit/', get_job_posting_limit, name='get_job_posting_limit'),

    # Admin manage job posting
    path('admin_accept_job_posting/', admin_accept_job_posting, name='admin_accept_job_posting'),
    path('admin_reject_job_posting/', admin_reject_job_posting, name='admin_reject_job_posting'),
    path('admin_get_list_job_posting/', AdminListJobPostingView.as_view(), name='admin_get_list_job_posting'),
]