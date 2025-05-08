from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from user.models import User

class UserAPITestCase(APITestCase):

    def setUp(self):
        self.signup_url = reverse('user_create')  # 예: path("user/signup/", views.SignUpView, name="user-signup")
        self.login_url = reverse('login')    # 예: path("user/login/", views.LoginView, name="user-login")

        self.signup_data = {
            "account": "testuser",
            "password": "testpass123",
            "age": 25,
            "gender": "male",
            "address": "Seoul",
            "name": "홍길동"
        }

        self.user = User.objects.create(
            account="existinguser",
            password=make_password("securepass123"),
            age=30,
            gender="female",
            address="Busan",
            name="김유진"
        )

    def test_user_signup(self):
        response = self.client.post(self.signup_url, self.signup_data, format='json')
        print("응답 코드:", response.status_code)
        print("응답 내용:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.filter(account="testuser").exists(), False)

    def test_user_login_success(self):
        response = self.client.post(self.login_url, {
            "account": "existinguser",
            "password": "securepass123"
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)  # JWT 토큰 반환한다고 가정

    def test_user_login_failure(self):
        response = self.client.post(self.login_url, {
            "account": "existinguser",
            "password": "wrongpass"
        }, format='json')
        self.assertEqual(response.status_code, 400)

