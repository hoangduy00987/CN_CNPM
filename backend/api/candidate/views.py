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


class CandidateBasicProfileView(APIView):
    serializer_class = CandidateBasicProfileSerializer
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
                data['message'] = 'Update candidate basic profile successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("update candidate profile error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class CandidateAdvancedProfileView(APIView):
    serializer_class = CandidateAdvancedProfileSerializer
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
                data['message'] = 'Update candidate advanced profile successfully.'
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
        
class CVCandidateView(APIView):
    serializer_class =CVCandidateSerializer
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
                serializer.upload_cv(request)
                data['message'] = 'CV upload successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("upload candidate cv error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try:
            model = CandidateProfile.objects.get(user=request.user)
            if model.cv:
                model.cv.delete()  
                model.cv = None  
                model.save()  
                return Response({"message": "CV deleted successfuly."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "CV not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            print("delete_cv_error: ", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== Admin =======================
class AdminManageCandidateMVS(viewsets.ModelViewSet):
    serializer_class = AdminManageCandidateSerializer
    permission_classes = [IsAdminUser]

    @action(methods=['GET'], detail=False, url_path='admin_get_number_of_candidate', url_name='admin_get_number_of_candidate')
    def admin_get_number_of_candidate(self, request):
        count = CandidateProfile.objects.count()
        return Response({
            "number_candidate": count
        })
    
    @action(methods=['POST'], detail=False, url_path='admin_block_candidate', url_name='admin_block_candidate')
    def admin_block_candidate(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.block(request)
                return Response({"message": "Block candidate successfully."})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False, url_path='admin_activate_candidate', url_name='admin_activate_candidate')
    def admin_activate_candidate(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.activate(request)
                return Response({"message": "Activate candidate successfully."})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    