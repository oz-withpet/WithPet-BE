from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import CustomUser


class SignupAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse("auth-signup")
        self.valid_payload = {
            "email": "test@example.com",
            "nickname": "테스트닉",
            "password": "TestPassword123!",
            "password2": "TestPassword123!",
            "pet_type": "dog",
            "gender": "female"
        }

    def test_signup_success(self):
        """✅ 정상 회원가입"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email=self.valid_payload["email"]).exists())

    def test_signup_password_mismatch(self):
        """❌ 비밀번호 불일치"""
        payload = self.valid_payload.copy()
        payload["password2"] = "Different123!"
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_signup_missing_email(self):
        """❌ 이메일 누락"""
        payload = self.valid_payload.copy()
        payload.pop("email")
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_signup_duplicate_email(self):
        """❌ 이메일 중복"""
        CustomUser.objects.create_user(
            email="test@example.com",
            nickname="다른닉",
            password="TestPassword123!"
        )
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_signup_duplicate_nickname(self):
        """❌ 닉네임 중복"""
        CustomUser.objects.create_user(
            email="unique@example.com",
            nickname="테스트닉",
            password="TestPassword123!"
        )
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)

    @patch("apps.users.serializers.contains_profanity", return_value=True)
    def test_signup_nickname_with_profanity(self, mock_contains_profanity):
        """❌ 닉네임에 비속어 포함"""
        payload = self.valid_payload.copy()
        payload["nickname"] = "비속어닉네임"
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)
        mock_contains_profanity.assert_called_once()

    @patch("apps.users.serializers.contains_profanity", return_value=True)
    def test_signup_email_with_profanity(self, mock_contains_profanity):
        """❌ 이메일에 비속어 포함"""
        payload = self.valid_payload.copy()
        payload["email"] = "욕설@example.com"
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        mock_contains_profanity.assert_called_once()
