from rest_framework import serializers
from ..submodels.models_recruitment import *
from ..candidate.serializers import CandidateBasicProfileSerializer
from django.core.mail import send_mail
from django.conf import settings
from ..options.serializers import *
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from .helpers import create_google_meet_event, update_google_calendar_event, delete_google_calendar_event
from django.utils import timezone

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'avatar', 'hotline', 'website', 'founded_year']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

class JobSearchSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    avatar_company = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_type',
            'title',
            'skill_required',
            'benefits',
            'location',
            'specific_address',
            'salary_range',
            'status',
            'level',
            'contract_type',
            'created_at',
            'updated_at',
            'avatar_company',
            'expired_at',
            'is_expired'
        ]

    def get_company(self, obj):
        return obj.company.name
    
    def get_avatar_company(self, obj):
        request = self.context.get('request')
        if obj.company.avatar and request:
            return request.build_absolute_uri(obj.company.avatar.url)
        return None

class PublicJobListOfCompanySerializer(serializers.ModelSerializer):
    avatar_company = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'job_type',
            'title',
            'skill_required',
            'location',
            'specific_address',
            'salary_range',
            'status',
            'level',
            'contract_type',
            'created_at',
            'updated_at',
            'avatar_company',
            'expired_at',
            'is_expired',
        ]

    def get_avatar_company(self, obj):
        request = self.context.get('request')
        if obj.company.avatar and request:
            return request.build_absolute_uri(obj.company.avatar.url)
        return None
    
class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    avatar_company = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_type',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'specific_address',
            'salary_range',
            'status',
            'level',
            'minimum_years_of_experience',
            'role_and_responsibilities',
            'contract_type',
            'interview_process',
            'created_at',
            'updated_at',
            'avatar_company',
            'expired_at',
            'is_expired',
        ]

    def get_avatar_company(self, obj):
        request = self.context.get('request')
        if obj.company.avatar and request:
            return request.build_absolute_uri(obj.company.avatar.url)
        return None

class JobListOfCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id',
            'job_type',
            'title',
            'skill_required',
            'benefits',
            'location',
            'specific_address',
            'salary_range',
            'status',
            'level',
            'created_at',
            'updated_at',
            'expired_at',
            'is_expired',
            'rejection_reason',
            'approved_at'
        ]

class JobManagementSerializer(serializers.ModelSerializer):
    is_posted = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = [
            "id",
            "job_type",
            "title",
            "description",
            "skill_required",
            "benefits",
            "location",
            "specific_address",
            "salary_range",
            "status",
            "level",
            "minimum_years_of_experience",
            "role_and_responsibilities",
            "contract_type",
            "interview_process",
            "expired_at",
            "is_posted"
        ]

    def get_is_posted(self, obj):
        if obj.status != Job.STATUS_DRAFT:
            return True
        return False

    def add(self, request):
        try:
            company = Company.objects.get(user=request.user)
            job_type = self.validated_data['job_type']
            title = self.validated_data['title']
            description = self.validated_data['description']
            skill_required = self.validated_data['skill_required']
            benefits = self.validated_data['benefits']
            location = self.validated_data['location']
            specific_address = self.validated_data['specific_address']
            salary_range = self.validated_data['salary_range']
            level = self.validated_data['level']
            minimum_years_of_experience = self.validated_data['minimum_years_of_experience']
            role_and_responsibilities = self.validated_data['role_and_responsibilities']
            contract_type = self.validated_data['contract_type']
            interview_process = self.validated_data['interview_process']
            expired_at = self.validated_data['expired_at']
            job = Job.objects.create(
                company=company,
                job_type=job_type,
                title=title,
                description=description,
                skill_required=skill_required,
                benefits=benefits,
                location=location,
                specific_address=specific_address,
                salary_range=salary_range,
                status=Job.STATUS_DRAFT,
                level=level,
                minimum_years_of_experience=minimum_years_of_experience,
                role_and_responsibilities=role_and_responsibilities,
                contract_type=contract_type,
                interview_process=interview_process,
                expired_at=expired_at
            )
            return job
        except Exception as error:
            print('add_job_error:', error)
            return None
        
    def add_and_post(self, request):
        try:
            company = Company.objects.get(user=request.user)
            job_type = self.validated_data['job_type']
            title = self.validated_data['title']
            description = self.validated_data['description']
            skill_required = self.validated_data['skill_required']
            benefits = self.validated_data['benefits']
            location = self.validated_data['location']
            specific_address = self.validated_data['specific_address']
            salary_range = self.validated_data['salary_range']
            level = self.validated_data['level']
            minimum_years_of_experience = self.validated_data['minimum_years_of_experience']
            role_and_responsibilities = self.validated_data['role_and_responsibilities']
            contract_type = self.validated_data['contract_type']
            interview_process = self.validated_data['interview_process']
            expired_at = self.validated_data['expired_at']
            job = Job.objects.create(
                company=company,
                job_type=job_type,
                title=title,
                description=description,
                skill_required=skill_required,
                benefits=benefits,
                location=location,
                specific_address=specific_address,
                salary_range=salary_range,
                status=Job.STATUS_PENDING,
                level=level,
                minimum_years_of_experience=minimum_years_of_experience,
                role_and_responsibilities=role_and_responsibilities,
                contract_type=contract_type,
                interview_process=interview_process,
                expired_at=expired_at
            )
            return job
        except Exception as error:
            print('add_and_post_job_error:', error)
            return None
        
    def save_changes(self, request):
        try:
            company = Company.objects.get(user=request.user)
            job_type = self.validated_data['job_type']
            title = self.validated_data['title']
            description = self.validated_data['description']
            skill_required = self.validated_data['skill_required']
            benefits = self.validated_data['benefits']
            location = self.validated_data['location']
            specific_address = self.validated_data['specific_address']
            salary_range = self.validated_data['salary_range']
            level = self.validated_data['level']
            minimum_years_of_experience = self.validated_data['minimum_years_of_experience']
            role_and_responsibilities = self.validated_data['role_and_responsibilities']
            contract_type = self.validated_data['contract_type']
            interview_process = self.validated_data['interview_process']
            expired_at = self.validated_data['expired_at']
            job_id = request.data.get('job_id')
            job = Job.objects.get(pk=job_id, company=company)
            job.job_type = job_type
            job.title = title
            job.description = description
            job.skill_required = skill_required
            job.benefits = benefits
            job.location = location
            job.specific_address = specific_address
            job.salary_range = salary_range
            job.level = level
            job.minimum_years_of_experience = minimum_years_of_experience
            job.role_and_responsibilities = role_and_responsibilities
            job.contract_type = contract_type
            job.interview_process = interview_process
            job.expired_at = expired_at
            job.save()
            return job
        except Exception as error:
            print('save_changes_job_error:', error)
            return None
        
    def save_and_post(self, request):
        try:
            company = Company.objects.get(user=request.user)
            job_type = self.validated_data['job_type']
            title = self.validated_data['title']
            description = self.validated_data['description']
            skill_required = self.validated_data['skill_required']
            benefits = self.validated_data['benefits']
            location = self.validated_data['location']
            specific_address = self.validated_data['specific_address']
            salary_range = self.validated_data['salary_range']
            level = self.validated_data['level']
            minimum_years_of_experience = self.validated_data['minimum_years_of_experience']
            role_and_responsibilities = self.validated_data['role_and_responsibilities']
            contract_type = self.validated_data['contract_type']
            interview_process = self.validated_data['interview_process']
            expired_at = self.validated_data['expired_at']
            job_id = request.data.get('job_id')
            job = Job.objects.get(pk=job_id, company=company)
            job.job_type = job_type
            job.title = title
            job.description = description
            job.skill_required = skill_required
            job.benefits = benefits
            job.location = location
            job.specific_address = specific_address
            job.salary_range = salary_range
            job.level = level
            job.minimum_years_of_experience = minimum_years_of_experience
            job.role_and_responsibilities = role_and_responsibilities
            job.contract_type = contract_type
            job.interview_process = interview_process
            job.expired_at = expired_at
            job.status = Job.STATUS_PENDING
            job.save()
            return job
        except Exception as error:
            print('save_and_post_job_error:', error)
            return None

class JobPostSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    job_type = serializers.PrimaryKeyRelatedField(queryset=JobType.objects.all())

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_type',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'salary_range',
            'status',
            'level',
            'minimum_years_of_experience',
            'interview_process',
            'expired_at'
        ]

    # def validate_salary_range(self, value):
    #     # Salary range format: min-max USD
    #     import re
    #     pattern = r'^\d+-\d+ USD$'
    #     if not re.match(pattern, value):
    #         raise serializers.ValidationError("Salary range must be in 'min-max USD', example: '1000-2000 USD'.")
    #     return value
    
    def create(self, request):
        try:
            validated_data = self.validated_data
            model = Job.objects.create(**validated_data)
            return model
        except Exception as error:
            print("post job error:", error)
            return None
        

class JobUpdateSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    job_type = serializers.PrimaryKeyRelatedField(queryset=JobType.objects.all())

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_type',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'salary_range',
            'status',
            'level',
            'minimum_years_of_experience',
            'interview_process',
            'expired_at'
        ]

    def validate_salary_range(self, value):
        # Salary range format: min-max USD
        import re
        pattern = r'^\d+-\d+ USD$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Salary range must be in 'min-max USD', example: '1000-2000 USD'.")
        return value
    
class ApplyJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'candidate', 'job', 'cv', 'applied_at', 'is_urgent']

    def check_existed_application(self, request, job_id):
        try:
            candidate = CandidateProfile.objects.get(user=request.user)
            application = Application.objects.get(candidate=candidate, job=job_id)
            return True
        except Application.DoesNotExist:
            return False

class ApplicationInforSerializer(serializers.ModelSerializer):
    candidate = CandidateBasicProfileSerializer()
    
    class Meta:
        model = Application
        fields = ['id', 'candidate', 'cv', 'applied_at', 'is_urgent', 'status', 'is_seen_by_recruiter']

class JobFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobFollow
        fields = ['id', 'job', 'candidate', 'is_notified']

class ListJobFollowSerializer(serializers.ModelSerializer):
    job_id = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    class Meta:
        model = JobFollow
        fields = ['id', 'job_id', 'job_title', 'company']

    def get_job_id(self, obj):
        return obj.job.id

    def get_job_title(self, obj):
        return obj.job.title
    
    def get_company(self, obj):
        return obj.job.company.name

class InterviewInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewInformation
        fields = ['id', 'interview_type', 'time_interview', 'date_interview', 'address', 'duration', 'note', 'meet_link']

    def add(self, request):
        try:
            candidate_id = request.data.get('candidate_id')
            job_id = request.data.get('job_id')
            candidate = CandidateProfile.objects.get(id=candidate_id)
            company = Company.objects.get(user=request.user)
            job = Job.objects.get(pk=job_id)
            interview_type = self.validated_data['interview_type']
            time_interview = self.validated_data['time_interview']
            date_interview = self.validated_data['date_interview']
            duration = self.validated_data['duration']
            note = self.validated_data['note']

            accept_url = f"http://localhost:8000{reverse('interview_response')}?response=accept"
            refuse_url = f"http://localhost:8000{reverse('interview_response')}?response=refuse"

            context = {
                'job_title': job.title,
                'candidate_name': candidate.full_name,
                'company_name': company.name,
                'interview_date': date_interview,
                'interview_time': time_interview,
                'duration': duration,
                'accept_url': accept_url,
                'refuse_url': refuse_url,
                'sender_name': 'HR Department',
                'sender_position': 'Admin - HR Division',
                'contact_information': company.user.email,
                'is_created': True
            }
            if interview_type.lower() == 'offline':
                address = self.validated_data['address']
                model = InterviewInformation.objects.create(
                    candidate=candidate,
                    company=company,
                    interview_type=InterviewInformation.OFFLINE,
                    time_interview=time_interview,
                    date_interview=date_interview,
                    address=address,
                    duration=duration,
                    note=note
                )
                context['interview_location'] = address
                context['is_online'] = False
            else:
                model = InterviewInformation.objects.create(
                    candidate=candidate,
                    company=company,
                    interview_type=InterviewInformation.ONLINE,
                    time_interview=time_interview,
                    date_interview=date_interview,
                    duration=duration,
                    note=note
                )
                datetime_itv = timezone.datetime.combine(model.date_interview, model.time_interview)
                datetime_itv = timezone.make_aware(datetime_itv)
                date_itv = timezone.localtime(datetime_itv).date()
                time_itv = timezone.localtime(datetime_itv).time()
                result = create_google_meet_event(
                    candidate_name=candidate.full_name,
                    interview_date=date_itv,
                    interview_time=time_itv,
                    duration=duration,
                    interviewer_email=candidate.user.email
                )
                context['interview_location'] = result['meet_link'] if result['meet_link'] else "To be announced"
                context['is_online'] = True
                model.event_id = result['event_id'] if result['event_id'] else None
                model.meet_link = result['meet_link'] if result['meet_link'] else None
                model.save()
            
            email_body = render_to_string('emails/interview_invitation.html', context)
            interview_email = EmailMessage(
                subject='Interview Invitation',
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[candidate.user.email]
            )
            interview_email.content_subtype = "html"
            interview_email.send()
            return model
        except Exception as error:
            print('add_interview_error:', error)
            return None
    
    def update(self, request):
        try:
            interview_id = request.data.get('interview_id')
            candidate_id = request.data.get('candidate_id')
            job_id = request.data.get('job_id')
            interview = InterviewInformation.objects.get(pk=interview_id)
            candidate = CandidateProfile.objects.get(id=candidate_id)
            company = Company.objects.get(user=request.user)
            job = Job.objects.get(pk=job_id)
            interview_type = self.validated_data['interview_type']
            time_interview = self.validated_data['time_interview']
            date_interview = self.validated_data['date_interview']
            duration = self.validated_data['duration']
            note = self.validated_data['note']

            context = {
                'job_title': job.title,
                'candidate_name': candidate.full_name,
                'company_name': company.name,
                'interview_date': date_interview,
                'interview_time': time_interview,
                'duration': duration,
                'sender_name': 'HR Department',
                'sender_position': 'Admin - HR Division',
                'contact_information': company.user.email,
                'is_created': False
            }
            if interview_type.lower() == 'offline':
                address = self.validated_data['address']
                interview.interview_type = InterviewInformation.OFFLINE
                interview.time_interview = time_interview
                interview.date_interview = date_interview
                interview.address = address
                interview.note = note
                if interview.event_id:
                    delete_google_calendar_event(event_id=interview.event_id)
                    interview.event_id = None
                    interview.meet_link = None
                interview.save()
                context['interview_location'] = address
                context['is_online'] = False
            else:
                interview.interview_type = InterviewInformation.ONLINE
                interview.time_interview = time_interview
                interview.date_interview = date_interview
                interview.duration = duration
                interview.note = note
                interview.address = None
                datetime_itv = timezone.datetime.combine(interview.date_interview, interview.time_interview)
                datetime_itv = timezone.make_aware(datetime_itv)
                date_itv = timezone.localtime(datetime_itv).date()
                time_itv = timezone.localtime(datetime_itv).time()
                if interview.event_id:
                    update_google_calendar_event(
                        event_id=interview.event_id,
                        candidate_name=candidate.full_name,
                        interview_date=date_itv,
                        interview_time=time_itv,
                        duration=duration
                    )
                    context['interview_location'] = interview.meet_link if interview.meet_link else "To be announced"
                else:
                    result = create_google_meet_event(
                        candidate_name=candidate.full_name,
                        interview_date=date_itv,
                        interview_time=time_itv,
                        duration=duration,
                        interviewer_email=candidate.user.email
                    )
                    context['interview_location'] = result['meet_link'] if result['meet_link'] else "To be announced"
                    interview.event_id = result['event_id'] if result['event_id'] else None
                    interview.meet_link = result['meet_link'] if result['meet_link'] else None
                interview.save()
                context['is_online'] = True
            
            email_body = render_to_string('emails/interview_invitation.html', context)
            interview_email = EmailMessage(
                subject='Interview Invitation',
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[candidate.user.email]
            )
            interview_email.content_subtype = "html"
            interview_email.send()
            return interview
        except Exception as error:
            print('update_interview_error:', error)
            return None

class JobPostingLimitOfCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPostingLimit
        fields = ['id', 'period', 'max_jobs', 'start_date', 'end_date']

# =============== Admin ===================
class AdminManageJobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'rejection_reason']

    def accept_job_posting(self, request):
        try:
            job_id = request.data.get('job_id')
            job = Job.objects.get(pk=job_id)
            job.status = Job.STATUS_APPROVED
            job.rejection_reason = None
            job.approved_at = timezone.localtime(timezone.now())
            job.save()
            return job
        except Exception as error:
            print("accepting_job_error:", error)
            return None
    
    def reject_job_posting(self, request):
        try:
            job_id = request.data.get('job_id')
            validated_data = self.validated_data
            job = Job.objects.get(pk=job_id)
            job.status = Job.STATUS_REJECTED
            job.rejection_reason = validated_data['rejection_reason']
            job.approved_at = timezone.localtime(timezone.now())
            job.save()
            return job
        except Exception as error:
            print("rejecting_job_error:", error)
            return None

class AdminListJobPostingSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    job_type = JobTypeSerializer(read_only=True)
    avatar_company = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_type',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'salary_range',
            'status',
            'level',
            'minimum_years_of_experience',
            'interview_process',
            'created_at',
            'updated_at',
            'avatar_company',
            'expired_at',
            'rejection_reason'
        ]

    def get_avatar_company(self, obj):
        request = self.context.get('request')
        if obj.company.avatar and request:
            return request.build_absolute_uri(obj.company.avatar.url)
        return None
