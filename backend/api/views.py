from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google_auth_oauthlib.flow import Flow
from .job.helpers import CREDENTIALS_FILE, SCOPES
import os

# Create your views here.
@api_view(['GET'])
def google_oauth_callback(request):
    # Lấy mã code từ URL callback
    code = request.GET.get('code')
    if not code:
        return Response({"error": "Authorization code not provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Tạo một flow để trao đổi mã code với token
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri='http://localhost:8000/api/oauth/callback/'
        )
        flow.fetch_token(code=code)

        # Lấy thông tin credentials và lưu lại
        credentials = flow.credentials
        return Response({
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_in": credentials.expiry
        })
    except Exception as error:
        print("google_oauth_callback_error:", error)
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
