from rest_framework import serializers
from ..submodels.models_recruitment import *
from ..candidate.serializers import CandidateProfileSerializer

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
    job = JobSerializer(many=True)
    class Meta:
        model = JobFollow
        fields = ['id', 'job', 'candidate', 'is_notified']