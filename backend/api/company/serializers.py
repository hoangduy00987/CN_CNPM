from rest_framework import serializers
from ..submodels.models_recruitment import *

class CompanyProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'avatar', 'hotline', 'website', 'founded_year']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def update(self, request):
        try:
            validated_data = self.validated_data
            company = Company.objects.get(user=request.user)
            fields_to_update = ['name', 'description', 'hotline', 'website', 'founded_year']

            for field in fields_to_update:
                setattr(company, field, validated_data[field])

            company.save()
            return company
        except Exception as error:
            print("Update company profile error:", error)
            return None

class UploadCompanyAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(required=True)

    class Meta:
        model = Company
        fields = ['avatar']

    def update_avatar(self, request):
        try:
            avatar = self.validated_data["avatar"]
            model = Company.objects.get(user=request.user)
            model.avatar = avatar
            model.save()
            return model
        except Exception as error:
            print("update_company_avatar_error: ", error)
            return None
