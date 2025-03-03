from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, date, time, timedelta
import calendar


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_candidate_profile')
    full_name = models.CharField(max_length=100, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    is_male = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to="candidate_avatars/", null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    cv = models.FileField(upload_to="cv/", null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary = models.TextField(null=True, blank=True)
    skills = models.CharField(max_length=300,null=True,blank=True)
    work_experience = models.TextField(null=True, blank=True)
    education = models.CharField(max_length=300, blank=True, null=True)
    projects = models.TextField(null=True, blank=True)
    languages = models.CharField(max_length=300, null=True, blank=True)
    interests = models.CharField(max_length=300, null=True, blank=True)
    references = models.CharField(max_length=300, null=True, blank=True)
    activities = models.TextField(null=True, blank=True)
    certifications = models.TextField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    preferred_salary = models.CharField(max_length=30, null=True, blank=True)
    preferred_work_location = models.CharField(max_length=50, null=True, blank=True)
    years_of_experience = models.CharField(max_length=30, null=True, blank=True)
    is_seeking_job = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_company')
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="company_avatars/", null=True, blank=True)
    hotline = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    founded_year = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_first_login = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def can_post_job(self):
        """Check if company can post new job or not"""
        today = timezone.now().date()
        job_limit = JobPostingLimit.objects.filter(company=self).first()

        # Nếu chưa có hạn mức hoặc chu kỳ đã hết hạn, tạo mới hoặc cập nhật
        if not job_limit or job_limit.end_date < today:
            if not job_limit:
                job_limit = JobPostingLimit(company=self, period=JobPostingLimit.PERIOD_DAILY, max_jobs=5)  # Giới hạn 5 job/ngày
            job_limit.set_period_dates()
            job_limit.save()

        # Kiểm tra số lượng job đã đăng trong chu kỳ hiện tại
        start_datetime = datetime.combine(job_limit.start_date, time(0, 0, 0))
        end_datetime = datetime.combine(job_limit.end_date, time(23, 59, 59))
        start_range = timezone.make_aware(start_datetime)
        end_range = timezone.make_aware(end_datetime)
        jobs_in_period = Job.objects.filter(
            company=self,
            updated_at__range=[start_range, end_range],
            status=Job.STATUS_PENDING
        ).count()

        # Trả về True nếu còn trong hạn mức, False nếu đã đạt giới hạn
        return jobs_in_period < job_limit.max_jobs

    def __str__(self):
        return "Company: " + self.name
    
class Job(models.Model):
    # Status job
    STATUS_DRAFT = 'Draft'
    STATUS_PENDING = 'Pending'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_w_job')
    job_type = models.CharField(max_length=30, null=True, blank=True)
    title = models.CharField(max_length=2000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    skill_required = models.TextField(null=True, blank=True)
    benefits = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    specific_address = models.CharField(max_length=150, null=True, blank=True)
    salary_range = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        null=True,
        blank=True,
    )
    level = models.CharField(max_length=100, null=True, blank=True)
    minimum_years_of_experience = models.CharField(max_length=30, null=True, blank=True)
    role_and_responsibilities = models.TextField(null=True, blank=True)
    contract_type = models.CharField(max_length=30, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    interview_process = models.TextField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def is_job_matching_skill(self, profile):
        """Check if job is matching with any skill of candidate."""
        if profile.skills:
            skills_list = [skill.strip().lower() for skill in profile.skills.split(',')]
            # job_skills = [skill.strip().lower() for skill in job.skill_required.split(',')]
            skills_match = any(skill in self.skill_required.lower() for skill in skills_list)
            # level_match = job.level.lower() == profile.work_experience.lower()
            
            # return skills_match and level_match
            return skills_match
        return False
    
    def is_job_matching_salary(self, profile):
        if profile.preferred_salary:
            salary_match = True if self.salary_range == profile.preferred_salary else False
            return salary_match
        return False
    
    def is_job_matching_location(self, profile):
        if profile.preferred_work_location:
            location_match = True if self.location == profile.preferred_work_location else False
            return location_match
        return False
    
    def is_job_matching_yoe(self, profile):
        if profile.years_of_experience:
            yoe_match = True if self.minimum_years_of_experience == profile.years_of_experience else False
            return yoe_match
        return False

    def __str__(self):
        return self.title
    
class JobPostingLimit(models.Model):
    PERIOD_DAILY = 'Daily'
    PERIOD_WEEKLY = 'Weekly'
    PERIOD_MONTHLY = 'Monthly'

    PERIOD_CHOICES = [
        (PERIOD_DAILY, 'Daily'),
        (PERIOD_WEEKLY, 'Weekly'),
        (PERIOD_MONTHLY, 'Monthly'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_posting_limit')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    max_jobs = models.PositiveIntegerField(default=1)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def set_period_dates(self):
        """Set up start_date and end_date based on period"""
        today = date.today()
        if self.period == self.PERIOD_DAILY:
            self.start_date = today
            self.end_date = today
        elif self.period == self.PERIOD_WEEKLY:
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.start_date = start_of_week
            self.end_date = end_of_week
        elif self.period == self.PERIOD_MONTHLY:
            start_of_month = today.replace(day=1)
            last_day_of_month = calendar.monthrange(today.year, today.month)[1]
            end_of_month = today.replace(day=last_day_of_month)
            self.start_date = start_of_month
            self.end_date = end_of_month

    def __str__(self):
        return f"{self.company.name} has jobs limit: {str(self.max_jobs)} {self.period}"
    
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
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_w_application')
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
    is_seen_by_recruiter = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.candidate.full_name + " " + self.job.title

class JobFollow(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_w_follow')
    followed_at = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.candidate.full_name} is following {self.job.title}"
    
class InterviewInformation(models.Model):
    OFFLINE = 'Offline'
    ONLINE = 'Online'

    TYPE = [
        (OFFLINE, 'Offline'),
        (ONLINE, 'Online'),
    ]

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_w_interview', null=True, blank=True)
    interview_type = models.CharField(max_length=10, choices=TYPE, default=OFFLINE, null=True, blank=True)
    time_interview = models.TimeField(null=True, blank=True)
    date_interview = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    duration = models.PositiveIntegerField(default=0)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event_id = models.CharField(max_length=255, null=True, blank=True, unique=True, editable=False)
    meet_link = models.URLField(null=True, blank=True, editable=False)

    def __str__(self):
        return f'{self.candidate.full_name} will be interviewed at {str(self.time_interview)} {str(self.date_interview)}'
