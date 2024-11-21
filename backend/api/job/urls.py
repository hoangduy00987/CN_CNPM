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
view_cv_in_application = ApplicationInforMVS.as_view({
    'post': 'view_cv_in_application'
})
get_job_posting_limit = JobPostingLimitOfCompanyMVS.as_view({
    'get': 'get_job_posting_limit'
})
add_job = JobManagementMVS.as_view({
    'post': 'add_job'
})
add_and_post_job = JobManagementMVS.as_view({
    'post': 'add_and_post_job'
})
save_changes_job = JobManagementMVS.as_view({
    'patch': 'save_changes_job'
})
save_and_post_job = JobManagementMVS.as_view({
    'patch': 'save_and_post_job'
})
get_job_by_id = JobManagementMVS.as_view({
    'get': 'get_job_by_id'
})

# ========== Admin ============
admin_get_number_of_job_posting = AdminManageJobPostingMVS.as_view({
    'get': 'admin_get_number_of_job_posting'
})
admin_accept_job_posting = AdminManageJobPostingMVS.as_view({
    'post': 'admin_accept_job_posting'
})
admin_reject_job_posting = AdminManageJobPostingMVS.as_view({
    'post': 'admin_reject_job_posting'
})

urlpatterns = [
    path('search/', JobSearchView.as_view(), name='job_search'),
    path('job-list-of-company/', JobListOfCompanyView.as_view(), name='job_list_company'),
    path('detail-job/', JobDetailView.as_view(), name='detail_job'),
    path('apply/', JobApplicationView.as_view(), name='job_application'),
    path('get_application_infor/', get_application_infor, name='get_application_infor'),
    path('get_list_application_candidate/', get_list_application_candidate, name='get_list_application_candidate'),
    path('get_list_candidate_applied_for_job/', get_list_candidate_applied_for_job, name='get_list_candidate_applied_for_job'),
    path('check_candidate_applied_job/', check_candidate_applied_job, name='check_candidate_applied_job'),
    path('view_cv_in_application/', view_cv_in_application, name='view_cv_in_application'),
    path('approve_application/', ApproveApplicationView.as_view(), name='approve_application'),
    path('notifications_job/', NotificationListView.as_view(), name='notification-list'),
    path('follow/', FollowJobView.as_view(), name='follow_job'),
    path('user-get-list-follow-job/', ListJobFollowOfUserView.as_view(), name='user_get_list_follow_job'),
    path('add-interview-information/', AddInterviewInformationView.as_view(), name='add_interview_infor'),
    path('interview-response/', interview_response, name='interview_response'),
    path('get_job_posting_limit/', get_job_posting_limit, name='get_job_posting_limit'),

    path('add_job/', add_job, name='add_job'),
    path('add_and_post_job/', add_and_post_job, name='add_and_post_job'),
    path('save_changes_job/', save_changes_job, name='save_changes_job'),
    path('save_and_post_job/', save_and_post_job, name='save_and_post_job'),
    path('get_job_by_id/', get_job_by_id, name='get_job_by_id'),
    # path('update_job/', JobUpdateView.as_view(), name='update_job'),
    # path('post_job/', JobPostView.as_view(), name='post_job'),
    path('hide_job/', HideJobView.as_view(), name='hide_job'),

    # Public
    path('job_list_of_company_public/', PublicJobListOfCompanyView.as_view(), name='job_list_of_company_public'),
    path('top_outstanding_jobs/', TopOutstandingJobsView.as_view(), name='top_outstanding_jobs'),
    path('top_new_jobs/', TopNewJobsView.as_view(), name='top_new_jobs'),

    # Admin manage job posting
    path('admin_get_number_of_job_posting/', admin_get_number_of_job_posting, name='admin_get_number_of_job_posting'),
    path('admin_accept_job_posting/', admin_accept_job_posting, name='admin_accept_job_posting'),
    path('admin_reject_job_posting/', admin_reject_job_posting, name='admin_reject_job_posting'),
    path('admin_get_list_job_posting/', AdminListJobPostingView.as_view(), name='admin_get_list_job_posting'),
]
