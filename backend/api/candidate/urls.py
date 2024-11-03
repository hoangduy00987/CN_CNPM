from django.urls import path
from .views import *

admin_get_number_of_candidate = AdminManageCandidateMVS.as_view({
    'get': 'admin_get_number_of_candidate'
})
admin_get_list_candidate = AdminManageCandidateMVS.as_view({
    'get': 'admin_get_list_candidate'
})
admin_block_candidate = AdminManageCandidateMVS.as_view({
    'post': 'admin_block_candidate'
})
admin_activate_candidate = AdminManageCandidateMVS.as_view({
    'post': 'admin_activate_candidate'
})

urlpatterns = [
    path('basic-profile/', CandidateBasicProfileView.as_view(), name='candidate_basic_profile'),
    path('advanced-profile/', CandidateAdvancedProfileView.as_view(), name='candidate_advanced_profile'),
    path('upload-avatar/', UploadCandidateAvatarView.as_view(), name='upload_candidate_avatar'),
    path('manage_cv/', CVCandidateView.as_view(), name='manage_cv'),

    # Admin
    path('admin_get_number_of_candidate/', admin_get_number_of_candidate, name='admin_get_number_of_candidate'),
    path('admin_get_list_candidate/', admin_get_list_candidate, name='admin_get_list_candidate'),
    path('admin_block_candidate/', admin_block_candidate, name='admin_block_candidate'),
    path('admin_activate_candidate/', admin_activate_candidate, name='admin_activate_candidate'),
]
