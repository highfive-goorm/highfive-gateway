from django.test import TestCase

from gateway.user.user_service import create_user
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()


# Create your tests here.
class UserTest(TestCase):
    def UserCreateTest(self):
        data = {'account': '11111', 'password': '11111', 'age': 1, 'gender': '남'}
        result = create_user(data)
        self.assertEqual(result['account'], data['account'])
        self.assertTrue(check_password(result['password'], make_password(data['password'])))
        self.assertEqual(result['age'], data['age'])
        self.assertEqual(result['gender'], data['gender'])
