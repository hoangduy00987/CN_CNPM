from django.contrib import admin
from .submodels.models_recruitment import *
from .submodels.models_dropdown import *

# Register your models here.
admin.site.register(CandidateProfile)
admin.site.register(Company)

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Notification)
admin.site.register(JobFollow)
admin.site.register(InterviewInformation)
admin.site.register(JobPostingLimit)

admin.site.register(JobType)
admin.site.register(SalaryRangeItem)
admin.site.register(YoeItem)
admin.site.register(LevelItem)
admin.site.register(SkillItem)
admin.site.register(ContractType)
