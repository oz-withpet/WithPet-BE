from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import CustomUser


class SignupAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse("auth-signup")
        self.valid_payload = {
            "email": "test@example.com",
            "nickname": "테스트닉네임",
            "password": "TestPassword123!",
            "password2": "TestPassword123!",
            "pet_type": "dog",
            "gender": "female"
        }

    def test_signup_success(self):
        """✅ 회원가입 성공 테스트"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email=self.valid_payload["email"]).exists())

    def test_signup_password_mismatch(self):
        """❌ 비밀번호 불일치"""
        payload = self.valid_payload.copy()
        payload["password2"] = "different"
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
        """❌ 중복 이메일"""
        CustomUser.objects.create_user(
            email="test@example.com",
            nickname="중복닉네임",
            password="TestPassword123!"
        )
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
