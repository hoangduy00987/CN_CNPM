from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..submodels.models_user import PasswordResetToken
from ..submodels.models_recruitment import CandidateProfile, Company
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from unittest.mock import patch
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
import json
from datetime import timedelta

class RegisterViewTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('jwt')

    def test_register_candidate_success(self):
        data = {
            "username": "candidate_user",
            "password": "StrongPassword123",
            "email": "candidate@example.com",
            "user_role": "candidate"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username="candidate_user")
        self.assertTrue(CandidateProfile.objects.filter(user=user).exists())

    def test_register_company_success(self):
        data = {
            "username": "company_user",
            "password": "StrongPassword123",
            "email": "company@example.com",
            "user_role": "recruiter"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username="company_user")
        self.assertTrue(Company.objects.filter(user=user).exists())

    def test_register_existing_email(self):
        User.objects.create_user(username="existing_user", email="existing@example.com", password="password")
        data = {
            "username": "new_user",
            "password": "StrongPassword123",
            "email": "existing@example.com",
            "user_role": "candidate"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_existing_username(self):
        User.objects.create_user(username="existing_user", email="user1@example.com", password="password")
        data = {
            "username": "existing_user",
            "password": "StrongPassword123",
            "email": "newuser@example.com",
            "user_role": "recruiter"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

class LoginViewTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username="testuser", password="testpass123", email="testuser@example.com")

    def test_login_success(self):
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_wrong_credentials(self):
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_login_nonexistent_user(self):
        data = {
            "username": "nonexistent",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.change_password_url = reverse('change_password')
        self.user = User.objects.create_user(username="testuser", password="oldpassword123", email="testuser@example.com")
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456"
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword456"))

    def test_change_password_wrong_old_password(self):
        data = {
            "old_password": "wrongoldpassword",
            "new_password": "newpassword456"
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))

    def test_change_password_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456"
        }
        response = self.client.put(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.password_reset_request_url = reverse('password_reset_request')
        self.password_reset_confirm_url = reverse('password_reset_confirm')
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")

    @patch('api.login.views.send_mail')
    def test_password_reset_request_success(self, mock_send_mail):
        data = {
            "email": "testuser@example.com"
        }
        response = self.client.post(self.password_reset_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertTrue(PasswordResetToken.objects.filter(uid=self.user.pk).exists())
        mock_send_mail.assert_called_once()

    def test_password_reset_request_nonexistent_email(self):
        data = {
            "email": "nonexistent@example.com"
        }
        response = self.client.post(self.password_reset_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_password_reset_confirm_success(self):
        token = default_token_generator.make_token(self.user)
        reset_token = PasswordResetToken.objects.create(uid=self.user.pk, token=token)
        data = {
            "uid": self.user.pk,
            "token": token,
            "new_password": "newpassword456"
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        reset_token.refresh_from_db()
        self.assertTrue(reset_token.is_used)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword456"))

    def test_password_reset_confirm_invalid_token(self):
        token = "invalidtoken123"
        PasswordResetToken.objects.create(uid=self.user.pk, token=token)
        data = {
            "uid": self.user.pk,
            "token": token,
            "new_password": "newpassword456"
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_password_reset_confirm_used_token(self):
        token = default_token_generator.make_token(self.user)
        reset_token = PasswordResetToken.objects.create(uid=self.user.pk, token=token, is_used=True)
        data = {
            "uid": self.user.pk,
            "token": token,
            "new_password": "newpassword456"
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_password_reset_confirm_nonexistent_user(self):
        token = default_token_generator.make_token(self.user)
        PasswordResetToken.objects.create(uid=999, token=token)
        data = {
            "uid": 999,
            "token": token,
            "new_password": "newpassword456"
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

class GoogleViewTests(APITestCase):
    def setUp(self):
        self.google_url = reverse('google')

    @patch('api.login.views.requests.get')
    def test_google_login_success_existing_user(self, mock_requests_get):
        # Mock response từ Google
        mock_response = {
            "email": "testuser@example.com",
            "name": "Test User"
        }
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = mock_response

        # Tạo user trước đó
        user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password123")

        data = {
            "token_google": "valid_google_token",
            "user_role": "candidate"
        }
        response = self.client.post(self.google_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('is_first_login', response.data)
        # Kiểm tra không tạo profile mới vì user đã tồn tại
        self.assertFalse(CandidateProfile.objects.filter(user=user).exists())

    @patch('api.login.views.requests.get')
    def test_google_login_success_new_candidate_user(self, mock_requests_get):
        # Mock response từ Google
        mock_response = {
            "email": "newcandidate@example.com",
            "name": "New Candidate"
        }
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = mock_response

        data = {
            "token_google": "valid_google_token",
            "user_role": "candidate"
        }
        response = self.client.post(self.google_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('is_first_login', response.data)
        user = User.objects.get(email="newcandidate@example.com")
        self.assertTrue(CandidateProfile.objects.filter(user=user).exists())

    @patch('api.login.views.requests.get')
    def test_google_login_invalid_token(self, mock_requests_get):
        # Mock response lỗi từ Google
        mock_requests_get.return_value.status_code = 400
        mock_requests_get.return_value.json.return_value = {"error": "invalid_token"}

        data = {
            "token_google": "invalid_token",
            "user_role": "recruiter"
        }
        response = self.client.post(self.google_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_google_login_missing_token(self):
        data = {
            "user_role": "candidate"
        }
        response = self.client.post(self.google_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

class CustomTokenRefreshViewTests(APITestCase):
    def setUp(self):
        self.token_refresh_url = reverse('token_refresh')
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        self.refresh = RefreshToken.for_user(self.user)

    def test_token_refresh_success(self):
        data = {
            "refresh": str(self.refresh)
        }
        response = self.client.post(self.token_refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        data = {
            "refresh": "invalidrefresh.token"
        }
        response = self.client.post(self.token_refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_token_refresh_expired_token(self):
        # Đây là ví dụ, thực tế cần cấu hình token với thời gian sống ngắn để test
        expired_refresh = RefreshToken.for_user(self.user)
        expired_refresh.set_exp(lifetime=timedelta(seconds=-1))  # Đặt thời gian hết hạn trong quá khứ
        data = {
            "refresh": str(expired_refresh)
        }
        response = self.client.post(self.token_refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

