from rest_framework import serializers
from ..submodels.models_recruitment import *

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'avatar', 'hotline', 'website', 'founded_year']

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'title', 'order']

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
    
    def update(self, request):
        try:
            validated_data = self.validated_data
            model = Job.objects.get(company__user=request.user)
            print('model:', model)
            fields_to_update = [
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

            for field in fields_to_update:
                setattr(model, field, validated_data[field])
            model.save()
            return model
        except Exception as error:
            print("update job error:", error)
            return None
