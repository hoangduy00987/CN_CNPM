
from django.urls import path,include
from .views import *

urlpatterns = [
    path('user/', include('api.login.urls')),
    path('candidate/', include('api.candidate.urls')),
    path('company/', include('api.company.urls')),
    path('job/', include('api.job.urls')),
    path('options/', include('api.options.urls')),

    # Google call back
    path('oauth/callback/', google_oauth_callback, name='google_oauth_callback'),
]
