from rest_framework.response import Response
from rest_framework import status, generics, filters, viewsets
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
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from ..submodels.models_user import *
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .serializers import *
from .filters import JobFilter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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
    
    def is_job_matching(self, profile, job):
        skills_list = [skill.strip().lower() for skill in profile.skills.split(',')]
        job_skills = [skill.strip().lower() for skill in job.skill_required.split(',')]
        skills_match = any(skill in skills_list for skill in job_skills)
        level_match = job.level.lower() == profile.level.lower()
        
        return skills_match and level_match

    def post(self, request):
        company = self.get_company(request.user)

        data = request.data.copy()
        data['company'] = company.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            job = serializer.save()
            users = User.objects.all()
            for user in users:
                try:
                    profile = CandidateProfile.objects.get(user=user)
                except CandidateProfile.DoesNotExist:
                    continue  # Bỏ qua người dùng này nếu không có hồ sơ
                if self.is_job_matching(profile, job):
                    Notification.objects.create(user=user, message=f"Có công việc mới phù hợp: {job.title}")
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
            if not job_id:
                return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            company = self.get_company(request.user)
            job = self.get_job(company, job_id)
            serializer = self.serializer_class(job, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['message'] = 'Recruitment is updated successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("updated job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        try:
            job_id = request.data.get('job_id')
            if not job_id:
                return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
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

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
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
            if not job_id:
                return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            company = self.get_company(request.user)
            job = self.get_job(company, job_id)
            job.is_deleted = True
            job.save()
            return Response({
                "message": "Hide job successfully."
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplyJobSerializer

    def get_candidate_profile(self, user):
        return get_object_or_404(CandidateProfile, user=user)
    
    def post(self, request):
        try:
            job_id = request.data.get('job_id')
            if not job_id:
                return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            candidate = self.get_candidate_profile(request.user)
            job = get_object_or_404(Job, pk=job_id, is_deleted=False)

            data = request.data.copy()
            data['candidate'] = candidate.id
            data['job'] = job.id
            data['applied_at'] = timezone.localtime(timezone.now())

            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                if not serializer.check_existed_application(request, job.id):
                    serializer.save()
                    return Response({
                        "message": "Applied job successfully.",
                        "result": serializer.data
                    }, status=status.HTTP_201_CREATED)
                return Response({"message": "You already applied this job."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("application create error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class ApplicationInforMVS(viewsets.ModelViewSet):
    serializer_class = ApplicationInforSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=["GET"], detail=True, url_path="get_application_infor", url_name="get_application_infor")
    def get_application_infor(self, request):
        try:
            application_id = request.query_params.get('application_id')
            if not application_id:
                return Response({"error": "application_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            data = Application.objects.get(pk=application_id)
            serializer = self.serializer_class(data, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("get_application_infor_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=["GET"], detail=False, url_path="get_list_application_candidate", url_name="get_list_application_candidate")
    def get_list_application_candidate(self, request):
        try:
            candidate = CandidateProfile.objects.get(user=request.user)
            applications = Application.objects.filter(candidate=candidate)
            serializer = self.serializer_class(applications, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("get_list_application_candidate_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=["GET"], detail=False, url_path="get_list_candidate_applied_for_job", url_name="get_list_candidate_applied_for_job")
    def get_list_candidate_applied_for_job(self, request):
        try:
            job_id = request.query_params.get('job_id')
            if not job_id:
                return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            applications = Application.objects.filter(job=job_id)
            serializer = self.serializer_class(applications, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("get_list_candidate_applied_for_job_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class ApproveApplicationView(APIView):
    serializer_class = ApplyJobSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            application_id = request.data.get('application_id')
            if not application_id:
                return Response({"error": "application_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            stt = request.data.get('status', Application.STATUS_REJECTED)
            application = Application.objects.get(pk=application_id)
            if stt.lower() == 'accepted':
                application.status = Application.STATUS_ACCEPTED
            else:
                application.status = Application.STATUS_REJECTED
            application.save()
            return Response({
                "message": f"{stt} successfully."
            }, status=status.HTTP_200_OK)
        except Exception as error:
            print("approve_application_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class FollowJobView(APIView):
    serializer_class = JobFollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            job_id = request.data.get('job_id')
            if not job_id:
                return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            job = Job.objects.get(pk=job_id)
            user = request.user

            job_follow, created = JobFollow.objects.get_or_create(
                job=job,
                candidate=user
            )

            if created:
                # Nếu vừa tạo theo dõi mới
                job_follow.is_notified = False
                job_follow.save()
                serializer = JobFollowSerializer(job_follow)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Nếu đã theo dõi, có thể hủy theo dõi
                job_follow.delete()
                return Response({"message": "Successfully unfollowed the job."}, status=status.HTTP_200_OK)

        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("follow_job_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        try:
            job_follow = JobFollow.objects.filter(candidate=request.user.id)
            serializer = self.serializer_class(job_follow, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    
        except Exception as error:
            print("follow_job_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

