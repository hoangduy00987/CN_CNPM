from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', CompanyProfileView.as_view(), name='company_profile'),
    path('upload-avatar/', UploadCompanyAvatarView.as_view(), name='upload_company_avatar'),
]