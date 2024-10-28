from django.urls import path
from .views import *

urlpatterns = [
    path('basic-profile/', CandidateBasicProfileView.as_view(), name='candidate_basic_profile'),
    path('advanced-profile/', CandidateAdvancedProfileView.as_view(), name='candidate_advanced_profile'),
    path('upload-avatar/', UploadCandidateAvatarView.as_view(), name='upload_candidate_avatar'),
    path('manage_cv/', CVCandidateView.as_view(), name='manage_cv'),
]