from django.contrib import admin
from .submodels.models_recruitment import *

# Register your models here.
admin.site.register(CandidateProfile)
admin.site.register(Company)
admin.site.register(JobCategory)
admin.site.register(Job)
admin.site.register(Application)
<<<<<<< HEAD
admin.site.register(Notification)
=======
admin.site.register(JobFollow)
>>>>>>> 01f433557fd9ec82cd6ea9a96fc9cd4e0f6dc059
