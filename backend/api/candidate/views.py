from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
import requests
from rest_framework.permissions import IsAuthenticated
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


class CandidateProfileView(APIView):
    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile = CandidateProfile.objects.get(user=user)
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
                data['message'] = 'Update candidate profile successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("update candidate profile error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class UploadCandidateAvatarView(APIView):
    serializer_class = UploadAvatarCandidateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.update_avatar(request)
                data['message'] = 'Upload candidate avatar successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("upload candidate avatar error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
