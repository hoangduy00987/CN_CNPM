from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
import requests
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from .serializers import *
from ..submodels.models_recruitment import *
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .serializers import *


class CompanyProfileView(APIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile = Company.objects.get(user=user)
            serializer = self.serializer_class(profile, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.update(request)
                data['message'] = 'Update company profile successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("update company profile error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class UploadCompanyAvatarView(APIView):
    serializer_class = UploadCompanyAvatarSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.update_avatar(request)
                data['message'] = 'Upload company avatar successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("upload company avatar error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        

# ===================== Admin ========================
class AdminManageCompanyMVS(viewsets.ModelViewSet):
    serializer_class = AdminManageCompanySerializer
    permission_classes = [IsAdminUser]

    @action(methods=['GET'], detail=False, url_path='admin_get_number_of_company', url_name='admin_get_number_of_company')
    def admin_get_number_of_company(self, request):
        count = Company.objects.count()
        return Response({
            "number_company": count
        })
    
    @action(methods=['GET'], detail=False, url_path='admin_get_list_company', url_name='admin_get_list_company')
    def admin_get_list_company(self, request):
        companys = Company.objects.all().order_by('id')
        serializer = self.serializer_class(companys, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(methods=['POST'], detail=False, url_path='admin_block_company', url_name='admin_block_company')
    def admin_block_company(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.block(request)
                return Response({"message": "Block company successfully."})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False, url_path='admin_activate_company', url_name='admin_activate_company')
    def admin_activate_company(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.activate(request)
                return Response({"message": "Activate company successfully."})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
