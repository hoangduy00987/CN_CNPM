from rest_framework import serializers
from ..submodels.models_recruitment import *

class CandidateBasicProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = CandidateProfile
        fields = ['id', 'full_name', 'birthday', 'is_male', 'avatar', 'phone_number', 'email', 'address']

    def get_email(self, obj):
        return obj.user.email
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def update(self, request):
        try:
            validated_data = self.validated_data
            profile = CandidateProfile.objects.get(user=request.user)
            fields_to_update = ['full_name', 'birthday', 'is_male', 'phone_number', 'address']

            for field in fields_to_update:
                setattr(profile, field, validated_data[field])

            profile.save()
            return profile
        except Exception as error:
            print("update_candidate_basic_profile_error:", error)
            return None
        
class CandidateAdvancedProfileSerializer(serializers.ModelSerializer):
    other_information = serializers.SerializerMethodField()
    class Meta:
        model = CandidateProfile
        fields = ['summary', 'skills', 'work_experience', 'education', 'projects', 'other_information']

    def get_other_information(self, obj):
        data = {}
        data['languages'] = obj.languages
        data['interests'] = obj.interests
        data['references'] = obj.references
        data['activities'] = obj.activities
        data['certifications'] = obj.certifications
        data['preferred_salary'] = obj.preferred_salary
        data['preferred_work_location'] = obj.preferred_work_location
        data['years_of_experience'] = obj.years_of_experience
        data['additional_info'] = obj.additional_info
        return data
    
    def update(self, request):
        try:
            validated_data = self.validated_data
            print(">>>", validated_data)
            additional_info = request.data.get('other_information')
            profile = CandidateProfile.objects.get(user=request.user)
            fields_to_update = ['summary', 'skills', 'work_experience', 'education', 'projects']
            fields_additional_info = ['languages', 'interests', 'references', 
                                      'activities', 'certifications', 'additional_info',
                                      'preferred_salary', 'preferred_work_location', 'years_of_experience']

            for field in fields_to_update:
                setattr(profile, field, validated_data[field])

            for field in fields_additional_info:
                setattr(profile, field, additional_info[field])

            profile.save()
            return profile
        except Exception as error:
            print("update_candidate_advanced_profile_error:", error)
            return None

class UploadAvatarCandidateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True)

    class Meta:
        model = CandidateProfile
        fields = ['avatar']

    def update_avatar(self,request):
        try:
            avatar = self.validated_data["avatar"]
            model = CandidateProfile.objects.get(user=request.user)
            model.avatar = avatar
            model.save()
            return model
        except Exception as error:
            print("update_candidate_avatar_error: ", error)
            return None
        
class CVCandidateSerializer(serializers.ModelSerializer):
    cv = serializers.FileField(required=True)

    class Meta:
        model = CandidateProfile
        fields = ['cv']

    def upload_cv(self,request):
        try:
            cv = self.validated_data["cv"]
            model = CandidateProfile.objects.get(user=request.user)
            model.cv = cv
            model.save()
            return model
        except Exception as error:
            print("update_candidate_cv_error: ", error)
            return None


# =============== Admin ======================
class AdminManageCandidateSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    class Meta:
        model = CandidateProfile
        fields = ['id', 'full_name', 'birthday', 'is_male', 'phone_number', 'email', 'address', 'is_active']

    def get_email(self, obj):
        return obj.user.email
    
    def block(self, request):
        try:
            email = request.data.get('email')
            user = User.objects.get(email=email)
            candidate = CandidateProfile.objects.get(user=user)
            user.is_active = False
            user.save()
            candidate.is_active = False
            candidate.save()
            return candidate
        except User.DoesNotExist:
            return None
        except CandidateProfile.DoesNotExist:
            return None
        except Exception as error:
            print('block_candidate_error:', error)
            return None
        
    def activate(self, request):
        try:
            email = request.data.get('email')
            user = User.objects.get(email=email)
            candidate = CandidateProfile.objects.get(user=user)
            user.is_active = True
            user.save()
            candidate.is_active = True
            candidate.save()
            return candidate
        except User.DoesNotExist:
            return None
        except CandidateProfile.DoesNotExist:
            return None
        except Exception as error:
            print('block_candidate_error:', error)
            return None
