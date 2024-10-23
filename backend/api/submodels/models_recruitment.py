from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    is_male = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to="candidate_avatars/", null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills  = models.CharField(max_length=255,null=True,blank=True)
    level = models.CharField(max_length=50, blank=True, null=True)
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return "Candidate: " + self.user.email + " " + self.full_name
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"
class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="company_avatars/", null=True, blank=True)
    hotline = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    founded_year = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return "Company: " + self.name
    
class JobCategory(models.Model):
    title = models.CharField(max_length=1000, null=True, blank=True)
    order = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=2000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    skill_required = models.TextField(null=True, blank=True)
    benefits = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    salary_range = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    level = models.CharField(max_length=100, null=True, blank=True)
    experience = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    interview_process = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_ACCEPTED = 'Accepted'
    STATUS_REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(null=True, blank=True)
    cv = models.FileField(upload_to="CVs/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return self.candidate.full_name + " " + self.job.title
