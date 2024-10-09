from rest_framework import serializers
from ..submodels.models_recruitment import *

class CandidateProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = CandidateProfile
        fields = ['id', 'full_name', 'is_male', 'avatar', 'phone_number', 'email']

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
            fields_to_update = ['full_name', 'is_male', 'phone_number']

            for field in fields_to_update:
                setattr(profile, field, validated_data[field])

            profile.save()
            return profile
        except Exception as error:
            print("Update candidate error:", error)
            return None
        

class UploadAvatarCandidateSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(required=True)

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

