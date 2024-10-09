from rest_framework.response import Response
from rest_framework import status, generics, filters
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
import requests
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from ..submodels.models_recruitment import *
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .serializers import *
from .filters import JobFilter


class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobSearchView(generics.ListAPIView):
    serializer_class = JobSerializer
    queryset = Job.objects.filter(is_deleted=False)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = [
        'title',
        'location',
        'skill_required',
        'company__name',
        'description',
    ]
    ordering_fields = ['created_at', 'salary_range', 'title']
    ordering = ['-created_at']
    pagination_class = JobPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

class JobCategoryListView(APIView):
    serializer_class = JobCategorySerializer
    
    def get(self, request):
        job_categories = JobCategory.objects.all()
        serializer = self.serializer_class(job_categories, many=True)
        return Response(serializer.data)


class JobPostView(APIView):
    serializer_class = JobPostSerializer
    permission_classes = [IsAuthenticated]

    def get_company(self, user):
        return get_object_or_404(Company, user=user)

    def post(self, request):
        company = self.get_company(request.user)

        data = request.data.copy()
        data['company'] = company.id

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class JobUpdateView(APIView):
    serializer_class = JobUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_company(self, user):
        return get_object_or_404(Company, user=user)
    
    def get_job(self, company, job_id):
        return get_object_or_404(Job, company=company, pk=job_id, is_deleted=False)

    def put(self, request):
        try:
            job_id = request.data.get('job_id')
            company = self.get_company(request.user)
            job = self.get_job(company, job_id)
            serializer = self.serializer_class(job, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.update(request)
                data['message'] = 'Recruitment is updated successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("updated job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        try:
            job_id = request.data.get('job_id')
            company = self.get_company(request.user)
            job = self.get_job(company, job_id)
            serializer = self.serializer_class(job, data=request.data, partial=True)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['message'] = 'Recruitment is updated successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("updated job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
class JobListOfCompanyView(APIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            company = get_object_or_404(Company, user=request.user)
            job_list = Job.objects.filter(company=company, is_deleted=False)
            serializer = self.serializer_class(job_list, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("error get list job of company:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class HideJobView(APIView):
    permission_classes = [IsAuthenticated]

    def get_company(self, user):
        return get_object_or_404(Company, user=user)
    
    def get_job(self, company, job_id):
        return get_object_or_404(Job, company=company, pk=job_id)

    def patch(self, request):
        try:
            job_id = request.data.get('job_id')
            company = self.get_company(request.user)
            job = self.get_job(company, job_id)
            job.is_deleted = True
            job.save()
            return Response({
                "message": "Hide job successfully."
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    