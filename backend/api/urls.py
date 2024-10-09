
from django.urls import path,include
from .views import *

urlpatterns = [
    path('user/', include('api.login.urls')),
    path('candidate/', include('api.candidate.urls')),
    path('company/', include('api.company.urls')),
    path('job/', include('api.job.urls')),
]
