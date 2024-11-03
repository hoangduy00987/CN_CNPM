from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from ..submodels.models_dropdown import *
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone


class SalaryRangeListView(APIView):
    serializer_class = SalaryRangeSerializer

    def get(self, request):
        salary_ranges = SalaryRangeItem.objects.all()
        serializer = self.serializer_class(salary_ranges, many=True)
        return Response(serializer.data)

class YoeListView(APIView):
    serializer_class = YoeSerializer

    def get(self, request):
        yoes = YoeItem.objects.all()
        serializer = self.serializer_class(yoes, many=True)
        return Response(serializer.data)

class LevelListView(APIView):
    serializer_class = LevelSerializer

    def get(self, request):
        levels = LevelItem.objects.all()
        serializer = self.serializer_class(levels, many=True)
        return Response(serializer.data)

class SkillListView(APIView):
    serializer_class = SkillSerializer

    def get(self, request):
        skills = SkillItem.objects.all()
        serializer = self.serializer_class(skills, many=True)
        return Response(serializer.data)

class JobTypeListView(APIView):
    serializer_class = JobTypeSerializer
    
    def get(self, request):
        job_types = JobType.objects.all()
        serializer = self.serializer_class(job_types, many=True)
        return Response(serializer.data)

class ContractTypeListView(APIView):
    serializer_class = ContractTypeSerializer

    def get(self, request):
        contract_types = ContractType.objects.all()
        serializer = self.serializer_class(contract_types, many=True)
        return Response(serializer.data)
