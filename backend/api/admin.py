from django.contrib import admin
from .submodels.models_recruitment import *

# Register your models here.
admin.site.register(CandidateProfile)
admin.site.register(Company)
admin.site.register(JobCategory)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Notification)
admin.site.register(JobFollow)
admin.site.register(InterviewInformation)
admin.site.register(JobPostingLimit)
