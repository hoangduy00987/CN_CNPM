from rest_framework import serializers
from ..submodels.models_dropdown import *

class SalaryRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryRangeItem
        fields = ['id', 'salary_range']

class YoeSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoeItem
        fields = ['id', 'yoe']

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelItem
        fields = ['id', 'level']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillItem
        fields = ['id', 'skill']

class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ['id', 'job_type']

class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ['id', 'contract_type']
