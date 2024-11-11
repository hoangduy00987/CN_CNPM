from rest_framework.response import Response
from rest_framework import status, generics, filters, viewsets
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import Q, Count
from rest_framework.views import APIView
import requests
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
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
from .filters import JobFilter

class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobSearchView(generics.ListAPIView):
    serializer_class = JobSearchSerializer
    queryset = Job.objects.filter(
        is_deleted=False, 
        status=Job.STATUS_APPROVED, 
        # expired_at__gt=timezone.now(), 
    )
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

class PublicJobListOfCompanyView(generics.ListAPIView):
    serializer_class = PublicJobListOfCompanySerializer
    pagination_class = JobPagination

    def get(self, request):
        try:
            company_id = request.query_params.get('company_id')
            company = Company.objects.get(pk=company_id)
            jobs_list = Job.objects.filter(company=company)

            page = self.paginate_queryset(jobs_list)
            if page is not None:
                serializer = self.serializer_class(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = self.serializer_class(jobs_list, many=True, context={'request': request})
            return Response(serializer.data)
        except Company.DoesNotExist:
            print("company not found")
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

class TopOutstandingJobsView(APIView):
    serializer_class = JobSearchSerializer

    def get(self, request):
        try:
            top_jobs = Job.objects.filter(
                is_deleted=False,
                status=Job.STATUS_APPROVED
            ).annotate(
                follow_count=Count('job_w_follow'),
                application_count=Count('job_w_application')
            ).order_by('-follow_count', '-application_count')[:10]
            serializer = self.serializer_class(top_jobs, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("error filter top outstanding jobs:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class TopNewJobsView(APIView):
    serializer_class = JobSearchSerializer

    def get(self, request):
        try:
            top_jobs = Job.objects.filter(
                is_deleted=False,
                status=Job.STATUS_APPROVED
            ).order_by('-created_at')[:10]
            serializer = self.serializer_class(top_jobs, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as error:
            print("error filter top new jobs:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class JobDetailView(APIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            job_id = request.query_params.get('job_id')
            job = Job.objects.get(pk=job_id)
            serializer = self.serializer_class(job)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            print('job_not_found')
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

class JobManagementMVS(viewsets.ModelViewSet):
    serializer_class = JobManagementSerializer
    permission_classes = [IsAuthenticated]

    def get_company(self, user):
        return get_object_or_404(Company, user=user)

    @action(methods=['GET'], detail=True, url_path='get_job_by_id', url_name='get_job_by_id')
    def get_job_by_id(self, request):
        try:
            job_id = request.query_params.get('job_id')
            job = Job.objects.get(pk=job_id)
            serializer = self.serializer_class(job)
            return Response(serializer.data)
        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path='add_job', url_name='add_job')
    def add_job(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                job = serializer.add(request)
                data = {}
                data['message'] = 'Add job successfully.'
                data['results'] = self.serializer_class(job).data
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("Add job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False, url_path='add_and_post_job', url_name='add_and_post_job')
    def add_and_post_job(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                job = serializer.add_and_post(request)
                data = {}
                data['message'] = 'Add and post job successfully.'
                data['results'] = self.serializer_class(job).data
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("Add job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['PATCH'], detail=False, url_path='save_changes_job', url_name='save_changes_job')
    def save_changes_job(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                job = serializer.save_changes(request)
                data = {}
                data['message'] = 'Save changes job successfully.'
                data['results'] = self.serializer_class(job).data
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("Save changes job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=['PATCH'], detail=False, url_path='save_and_post_job', url_name='save_and_post_job')
    def save_and_post_job(self, request):
        try:
            company = self.get_company(request.user)
            if not company.can_post_job():
                return Response({
                    "error": "You have reached your job posting limit for the current period."
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                job = serializer.save_and_post(request)
                data = {}
                data['message'] = 'Save and post job successfully.'
                data['results'] = self.serializer_class(job).data
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("Save and post job error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

# class JobPostView(APIView):
#     serializer_class = JobPostSerializer
#     permission_classes = [IsAuthenticated]

#     def get_company(self, user):
#         return get_object_or_404(Company, user=user)

#     def post(self, request):
#         try:
#             company = self.get_company(request.user)
#             if not company.can_post_job():
#                 return Response({
#                     "error": "You have reached your job posting limit for the current period."
#                 }, status=status.HTTP_406_NOT_ACCEPTABLE)

#             data = request.data.copy()
#             data['company'] = company.id

#             serializer = self.serializer_class(data=data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as error:
#             print("post job error:", error)
#             return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


# class JobUpdateView(APIView):
#     serializer_class = JobUpdateSerializer
#     permission_classes = [IsAuthenticated]

#     def get_company(self, user):
#         return get_object_or_404(Company, user=user)
    
#     def get_job(self, company, job_id):
#         return get_object_or_404(Job, company=company, pk=job_id, is_deleted=False)

#     def put(self, request):
#         try:
#             job_id = request.data.get('job_id')
#             if not job_id:
#                 return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
#             company = self.get_company(request.user)
#             job = self.get_job(company, job_id)
#             serializer = self.serializer_class(job, data=request.data)
#             data = {}
#             if serializer.is_valid():
#                 serializer.save()
#                 data['message'] = 'Recruitment is updated successfully.'
#                 return Response(data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as error:
#             print("updated job error:", error)
#             return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
#     def patch(self, request):
#         try:
#             job_id = request.data.get('job_id')
#             if not job_id:
#                 return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
#             company = self.get_company(request.user)
#             job = self.get_job(company, job_id)
#             serializer = self.serializer_class(job, data=request.data, partial=True)
#             data = {}
#             if serializer.is_valid():
#                 serializer.save()
#                 data['message'] = 'Recruitment is updated successfully.'
#                 return Response(data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as error:
#             print("updated job error:", error)
#             return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
class JobListOfCompanyView(APIView):
    serializer_class = JobListOfCompanySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            company = get_object_or_404(Company, user=request.user)
            job_list = Job.objects.filter(company=company, is_deleted=False).order_by('id')
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
        
    @action(methods=["GET"], detail=False, url_path="check_candidate_applied_job", url_name="check_candidate_applied_job")
    def check_candidate_applied_job(self, request):
        candidate = CandidateProfile.objects.get(user=request.user)
        job_id = request.query_params.get('job_id')
        results = Application.objects.filter(candidate=candidate, job=job_id)
        data = {}
        data['is_applied'] = False
        if len(results) > 0:
            data['is_applied'] = True
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='view_cv_in_application', url_name='view_cv_in_application')
    def view_cv_in_application(self, request):
        try:
            application_id = request.query_params.get('application_id')
            application = Application.objects.get(pk=application_id)
            application.is_seen_by_recruiter = True
            application.save()
            return Response({"message": "Recruiter has seen application."}, status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            print("application not found")
            return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

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
                notified_at = datetime.strftime(timezone.localtime(timezone.now()), "%Y-%m-%d %H:%M:%S")
                Notification.objects.create(
                    user=application.candidate.user,
                    message=f'Đơn ứng tuyển ở công việc {application.job.title} đã được phản hồi./application_id={application.id}/time: {notified_at}'
                )
            else:
                application.status = Application.STATUS_REJECTED
                notified_at = datetime.strftime(timezone.localtime(timezone.now()), "%Y-%m-%d %H:%M:%S")
                Notification.objects.create(
                    user=application.candidate.user,
                    message=f'Đơn ứng tuyển ở công việc {application.job.title} đã được phản hồi./application_id={application.id}/time:{notified_at}'
                )
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
            candidate = CandidateProfile.objects.get(user=user)

            job_follow, created = JobFollow.objects.get_or_create(
                job=job,
                candidate=candidate
            )

            if created:
                # Nếu vừa tạo theo dõi mới
                job_follow.is_notified = False
                job_follow.save()
                return Response({"message": f"Followed the job {job.title} successfully."}, status=status.HTTP_201_CREATED)
            else:
                # Nếu đã theo dõi, có thể hủy theo dõi
                job_follow.delete()
                return Response({"message": "Successfully unfollowed the job."}, status=status.HTTP_200_OK)

        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("follow_job_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        try:
            candidate = CandidateProfile.objects.get(user=request.user)
            job_follow = JobFollow.objects.filter(candidate=candidate)
            serializer = self.serializer_class(job_follow, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    
        except Exception as error:
            print("follow_job_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class ListJobFollowOfUserView(APIView):
    serializer_class = ListJobFollowSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            candidate = CandidateProfile.objects.get(user=request.user)
            follows = JobFollow.objects.filter(candidate=candidate)
            serializer = self.serializer_class(follows, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            print('get_list_follow_job_user_error:', error)
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

class AddInterviewInformationView(APIView):
    serializer_class = InterviewInformationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.add(request)
                data['message'] = 'Add interview information successfully.'
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class JobPostingLimitOfCompanyMVS(viewsets.ModelViewSet):
    serializer_class = JobPostingLimitOfCompanySerializer
    permission_classes = [IsAuthenticated]

    def get_company(self, user):
        return get_object_or_404(Company, user=user)

    @action(methods=['GET'], detail=True, url_path='get_job_posting_limit', url_name='get_job_posting_limit')
    def get_job_posting_limit(self, request):
        try:
            company = self.get_company(request.user)
            limit = JobPostingLimit.objects.get(company=company)
            serializer = self.serializer_class(limit)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            print("get_job_posting_limit_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

# ============ Admin ======================
class AdminManageJobPostingMVS(viewsets.ModelViewSet):
    serializer_class = AdminManageJobPostingSerializer
    permission_classes = [IsAdminUser]

    @action(methods=['GET'], detail=False, url_path='admin_get_number_of_job_posting', url_name='admin_get_number_of_job_posting')
    def admin_get_number_of_job_posting(self, request):
        count = Job.objects.filter(
            Q(is_deleted=False) &
            ~Q(status=Job.STATUS_DRAFT)
        ).count()
        return Response({
            "number_job_posting": count
        })

    @action(methods=['POST'], detail=False, url_path='admin_accept_job_posting', url_name='admin_accept_job_posting')
    def admin_accept_job_posting(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            data = {}
            if serializer.is_valid():
                job = serializer.accept_job_posting(request)
                data['message'] = 'Approved job posting successfully.'
                candidates = CandidateProfile.objects.all()
                for candidate in candidates:
                    condition = (job.status == Job.STATUS_APPROVED) and (job.expired_at > timezone.now()) and (job.is_deleted == False)
                    if job.is_job_matching(candidate) and condition:
                        Notification.objects.create(user=candidate.user, message=f"Có công việc mới phù hợp: {job.title}/job_id={job.id}")
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=['POST'], detail=False, url_path='admin_reject_job_posting', url_name='admin_reject_job_posting')
    def admin_reject_job_posting(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.reject_job_posting(request)
                data['message'] = 'Rejected job posting successfully.'
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class AdminListJobPostingView(APIView):
    serializer_class = AdminListJobPostingSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            jobs = Job.objects.filter(
                Q(is_deleted=False) &
                ~Q(status=Job.STATUS_DRAFT)
                # Q(expired_at__gt=timezone.now())
            )
            serializer = self.serializer_class(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            print("admin_get_list_job_to approve_error:", error)
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
