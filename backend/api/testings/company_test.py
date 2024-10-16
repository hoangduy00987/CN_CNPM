import tempfile
import shutil
import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..submodels.models_recruitment import Company
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from unittest.mock import patch

# Tạo một thư mục tạm thời cho MEDIA_ROOT trong quá trình testing
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

class CompanyProfileViewTests(APITestCase):
    def setUp(self):
        # Tạo user và Company profile
        self.user = User.objects.create_user(username='companyuser', password='testpass123', email='company@example.com')
        self.company = Company.objects.create(
            user=self.user,
            name='Test Company',
            description='A company for testing.',
            hotline='1234567890',
            website='https://www.testcompany.com',
            founded_year='2020-01-01'
        )
        self.url = reverse('company_profile')
        
        # Tạo token và xác thực
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_get_company_profile_success(self):
        """
        Kiểm tra GET /profile/ thành công
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Company')
        self.assertEqual(response.data['description'], 'A company for testing.')
        self.assertEqual(response.data['hotline'], '1234567890')
        self.assertEqual(response.data['website'], 'https://www.testcompany.com')
        self.assertEqual(response.data['founded_year'], '2020-01-01')
        self.assertIsNone(response.data['avatar'])  # Avatar chưa được tải lên

    def test_get_company_profile_unauthenticated(self):
        """
        Kiểm tra GET /profile/ không xác thực
        """
        self.client.credentials()  # Xóa token
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_update_company_profile_success(self):
        """
        Kiểm tra POST /profile/ cập nhật profile thành công
        """
        data = {
            "name": "Updated Company",
            "description": "Updated description.",
            "hotline": "0987654321",
            "website": "https://www.updatedcompany.com",
            "founded_year": "2021-05-15"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Update company profile successfully.')
        
        # Kiểm tra dữ liệu đã được cập nhật trong database
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Company')
        self.assertEqual(self.company.description, 'Updated description.')
        self.assertEqual(self.company.hotline, '0987654321')
        self.assertEqual(self.company.website, 'https://www.updatedcompany.com')
        self.assertEqual(str(self.company.founded_year), '2021-05-15')

    def test_post_update_company_profile_invalid_data(self):
        """
        Kiểm tra POST /profile/ với dữ liệu không hợp lệ (ví dụ: founded_year sai định dạng)
        """
        data = {
            "name": "Updated Company",
            "description": "Updated description.",
            "hotline": "0987654321",
            "website": "https://www.updatedcompany.com",
            "founded_year": "invalid-date"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('founded_year', response.data)

    def test_post_update_company_profile_partial_update(self):
        """
        Kiểm tra POST /profile/ cập nhật một phần của profile
        """
        data = {
            "description": "Partially updated description."
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Update company profile successfully.')
        
        self.company.refresh_from_db()
        self.assertEqual(self.company.description, 'Partially updated description.')
        self.assertEqual(self.company.name, 'Test Company')  # Không thay đổi
        self.assertEqual(self.company.hotline, '1234567890')  # Không thay đổi

    def test_post_update_company_profile_no_data(self):
        """
        Kiểm tra POST /profile/ với không có dữ liệu
        """
        data = {}
        response = self.client.post(self.url, data, format='json')
        # Tùy thuộc vào logic trong serializer.update, có thể cập nhật không gì hoặc báo lỗi
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Update company profile successfully.')
        # Không thay đổi gì
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Test Company')
        self.assertEqual(self.company.description, 'A company for testing.')
        self.assertEqual(self.company.hotline, '1234567890')
        self.assertEqual(self.company.website, 'https://www.testcompany.com')
        self.assertEqual(str(self.company.founded_year), '2020-01-01')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UploadCompanyAvatarViewTests(APITestCase):
    def setUp(self):
        # Tạo user và Company profile
        self.user = User.objects.create_user(username='companyuser', password='testpass123', email='company@example.com')
        self.company = Company.objects.create(
            user=self.user,
            name='Test Company',
            description='A company for testing.',
            hotline='1234567890',
            website='https://www.testcompany.com',
            founded_year='2020-01-01'
        )
        self.url = reverse('upload_company_avatar')
        
        # Tạo token và xác thực
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def tearDown(self):
        # Xóa thư mục tạm thời sau khi test xong
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @patch('api.company.views.UploadCompanyAvatarSerializer.update_avatar')
    def test_upload_avatar_success(self, mock_update_avatar):
        """
        Kiểm tra POST /upload-avatar/ tải avatar thành công (sử dụng mocking)
        """
        mock_update_avatar.return_value = self.company  # Giả lập việc cập nhật thành công
        
        # Tạo một file ảnh giả
        avatar = SimpleUploadedFile(
            "avatar.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        data = {
            "avatar": avatar
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Upload company avatar successfully.')
        mock_update_avatar.assert_called_once()

    def test_upload_avatar_success_actual_upload(self):
        """
        Kiểm tra POST /upload-avatar/ tải avatar thành công với upload thực tế
        """
        # Tạo một file ảnh giả
        avatar = SimpleUploadedFile(
            "avatar.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        data = {
            "avatar": avatar
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Upload company avatar successfully.')
        
        # Kiểm tra avatar đã được cập nhật trong database
        self.company.refresh_from_db()
        self.assertIsNotNone(self.company.avatar)
        self.assertTrue(self.company.avatar.name.endswith('avatar.jpg'))

        # Kiểm tra file thực tế đã tồn tại trong MEDIA_ROOT tạm thời
        self.assertTrue(self.company.avatar.path.startswith(TEMP_MEDIA_ROOT))
        self.assertTrue(os.path.exists(self.company.avatar.path))

    def test_upload_avatar_invalid_data(self):
        """
        Kiểm tra POST /upload-avatar/ với dữ liệu không hợp lệ (không gửi file)
        """
        data = {}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('avatar', response.data)

    def test_upload_avatar_unauthenticated(self):
        """
        Kiểm tra POST /upload-avatar/ không xác thực
        """
        self.client.credentials()  # Xóa token
        # Tạo một file ảnh giả
        avatar = SimpleUploadedFile(
            "avatar.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        data = {
            "avatar": avatar
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

