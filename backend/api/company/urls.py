from django.urls import path
from .views import *

admin_get_number_of_company = AdminManageCompanyMVS.as_view({
    'get': 'admin_get_number_of_company'
})
admin_get_list_company = AdminManageCompanyMVS.as_view({
    'get': 'admin_get_list_company'
})
admin_block_company = AdminManageCompanyMVS.as_view({
    'post': 'admin_block_company'
})
admin_activate_company = AdminManageCompanyMVS.as_view({
    'post': 'admin_activate_company'
})

urlpatterns = [
    path('profile/', CompanyProfileView.as_view(), name='company_profile'),
    path('upload-avatar/', UploadCompanyAvatarView.as_view(), name='upload_company_avatar'),

    # Public
    path('list_company/', ListCompanyView.as_view(), name='list_company'),
    path('company_information/', CompanyInformationView.as_view(), name='company_information'),
    path('top_outstanding_companies/', TopOutstandingCompaniesView.as_view(), name='top_outstanding_companies'),

    # Admin
    path('admin_get_number_of_company/', admin_get_number_of_company, name='admin_get_number_of_company'),
    path('admin_get_list_company/', admin_get_list_company, name='admin_get_list_company'),
    path('admin_block_company/', admin_block_company, name='admin_block_company'),
    path('admin_activate_company/', admin_activate_company, name='admin_activate_company'),
]
