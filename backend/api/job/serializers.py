from rest_framework import serializers
from ..submodels.models_recruitment import *
from ..candidate.serializers import CandidateProfileSerializer
from django.core.mail import send_mail
from django.conf import settings

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'avatar', 'hotline', 'website', 'founded_year']

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'title', 'order']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    job_category = JobCategorySerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_category',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'salary_range',
            'status',
            'level',
            'experience',
            'interview_process',
            'created_at',
            'updated_at',
            'avatar_url',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.company.avatar and request:
            return request.build_absolute_uri(obj.company.avatar.url)
        return None
    
class JobPostSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    job_category = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all())

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_category',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'salary_range',
            'status',
            'level',
            'experience',
            'interview_process',
        ]

    def validate_salary_range(self, value):
        # Salary range format: min-max USD
        import re
        pattern = r'^\d+-\d+ USD$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Salary range must be in 'min-max USD', example: '1000-2000 USD'.")
        return value
    
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
    job_category = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all())

    class Meta:
        model = Job
        fields = [
            'id',
            'company',
            'job_category',
            'title',
            'description',
            'skill_required',
            'benefits',
            'location',
            'salary_range',
            'status',
            'level',
            'experience',
            'interview_process',
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
    candidate = CandidateProfileSerializer()
    
    class Meta:
        model = Application
        fields = ['id', 'candidate', 'cv', 'applied_at', 'is_urgent', 'status']

class JobFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobFollow
        fields = ['id', 'job', 'candidate', 'is_notified']

class ListJobFollowSerializer(serializers.ModelSerializer):
    job_id = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    class Meta:
        model = JobFollow
        fields = ['id', 'job_id', 'job_title']

    def get_job_id(self, obj):
        return obj.job.id

    def get_job_title(self, obj):
        return obj.job.title

class InterviewInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewInformation
        fields = ['id', 'time_interview', 'date_interview', 'location', 'note']

    def add(self, request):
        try:
            candidate_id = request.data.get('candidate_id')
            candidate = CandidateProfile.objects.get(id=candidate_id)
            company = Company.objects.get(user=request.user)
            time_interview = self.validated_data['time_interview']
            date_interview = self.validated_data['date_interview']
            location = self.validated_data['location']
            note = self.validated_data['note']
            model = InterviewInformation.objects.create(
                candidate=candidate,
                company=company,
                time_interview=time_interview,
                date_interview=date_interview,
                location=location,
                note=note
            )
            send_mail(
                subject=f'Interview information from {company.name}',
                message=f'We are very happy to invite you to the upcoming interview\nTime: {time_interview} {date_interview}\nLocation: {location}\nNote: {note}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[candidate.user.email],
                fail_silently=False
            )
            return model
        except Exception as error:
            print('add_interview_error:', error)
            return None
