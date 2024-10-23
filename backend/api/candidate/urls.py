from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', CandidateProfileView.as_view(), name='candidate_profile'),
    path('upload-avatar/', UploadCandidateAvatarView.as_view(), name='upload_candidate_avatar'),
    path('manage_cv/', CVCandidateView.as_view(), name='manage_cv'),
]