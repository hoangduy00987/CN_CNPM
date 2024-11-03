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


# ======================== Admin ==============================
class AdminManageSalaryRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryRangeItem
        fields = ['id', 'salary_range']
    
class AdminManageYoeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoeItem
        fields = ['id', 'yoe']

class AdminManageLevelItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelItem
        fields = ['id', 'level', 'codename']

class AdminManageSkillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillItem
        fields = ['id', 'skill', 'codename']

class AdminManageJobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ['id', 'job_type', 'codename']

class AdminManageContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ['id', 'contract_type', 'codename']
