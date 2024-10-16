import tempfile
import shutil
import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..submodels.models_recruitment import CandidateProfile
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from unittest.mock import patch

# Tạo một thư mục tạm thời cho MEDIA_ROOT trong quá trình testing
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

class CandidateProfileViewTests(APITestCase):
    def setUp(self):
        # Tạo user và CandidateProfile
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='testuser@example.com')
        self.profile = CandidateProfile.objects.create(
            user=self.user,
            full_name='Test User',
            is_male=True,
            phone_number='1234567890'
        )
        self.url = reverse('candidate_profile')
        
        # Tạo token và xác thực
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_get_profile_success(self):
        """
        Kiểm tra GET /profile/ thành công
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Test User')
        self.assertEqual(response.data['is_male'], True)
        self.assertEqual(response.data['phone_number'], '1234567890')
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertIsNone(response.data['avatar'])  # Avatar chưa được tải lên

    def test_get_profile_unauthenticated(self):
        """
        Kiểm tra GET /profile/ không xác thực
        """
        self.client.credentials()  # Xóa token
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_update_profile_success(self):
        """
        Kiểm tra POST /profile/ cập nhật profile thành công
        """
        data = {
            "full_name": "Updated Name",
            "is_male": False,
            "phone_number": "0987654321"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Update candidate profile successfully.')
        
        # Kiểm tra dữ liệu đã được cập nhật trong database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Updated Name')
        self.assertEqual(self.profile.is_male, False)
        self.assertEqual(self.profile.phone_number, '0987654321')

    def test_post_update_profile_invalid_data(self):
        """
        Kiểm tra POST /profile/ với dữ liệu không hợp lệ
        """
        data = {
            "full_name": "",  # Giả sử full_name không được để trống
            "is_male": False,
            "phone_number": "0987654321"
        }
        response = self.client.post(self.url, data, format='json')
        # Tùy thuộc vào validate của serializer, có thể trả về lỗi
        # Trong trường hợp này, serializer không có validate cụ thể, nên cập nhật thành công
        # Tuy nhiên, nếu bạn thêm validate thì nên kiểm tra lỗi tương ứng
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, '')  # Nếu được phép

    def test_post_update_profile_partial_update(self):
        """
        Kiểm tra POST /profile/ cập nhật một phần của profile
        """
        data = {
            "full_name": "Partial Update"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Update candidate profile successfully.')
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Partial Update')
        self.assertEqual(self.profile.is_male, True)  # Không thay đổi
        self.assertEqual(self.profile.phone_number, '1234567890')  # Không thay đổi

    def test_post_update_profile_no_data(self):
        """
        Kiểm tra POST /profile/ với không có dữ liệu
        """
        data = {}
        response = self.client.post(self.url, data, format='json')
        # Tùy thuộc vào logic trong serializer.update, có thể cập nhật không gì hoặc báo lỗi
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Update candidate profile successfully.')
        # Không thay đổi gì
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Test User')
        self.assertEqual(self.profile.is_male, True)
        self.assertEqual(self.profile.phone_number, '1234567890')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UploadCandidateAvatarViewTests(APITestCase):
    def setUp(self):
        # Tạo user và CandidateProfile
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='testuser@example.com')
        self.profile = CandidateProfile.objects.create(
            user=self.user,
            full_name='Test User',
            is_male=True,
            phone_number='1234567890'
        )
        self.url = reverse('upload_candidate_avatar')
        
        # Tạo token và xác thực
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def tearDown(self):
        # Xóa thư mục tạm thời sau khi test xong
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @patch('api.candidate.views.UploadAvatarCandidateSerializer.update_avatar')
    def test_upload_avatar_success(self, mock_update_avatar):
        """
        Kiểm tra POST /upload-avatar/ tải avatar thành công
        """
        mock_update_avatar.return_value = self.profile  # Giả lập việc cập nhật thành công
        
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
        self.assertEqual(response.data['message'], 'Upload candidate avatar successfully.')
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
        self.assertEqual(response.data['message'], 'Upload candidate avatar successfully.')
        
        # Kiểm tra avatar đã được cập nhật trong database
        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.avatar)
        self.assertTrue(self.profile.avatar.name.endswith('avatar.jpg'))

        # Kiểm tra file thực tế đã tồn tại trong MEDIA_ROOT tạm thời
        self.assertTrue(self.profile.avatar.path.startswith(TEMP_MEDIA_ROOT))
        self.assertTrue(os.path.exists(self.profile.avatar.path))

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

