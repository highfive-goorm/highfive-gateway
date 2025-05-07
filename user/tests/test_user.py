from unittest import TestCase

from gateway.user.models import User

user = User()


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(account='testuser', password='password123')

    def test_user_exists(self):
        self.assertTrue(User.objects.filter(account='testuser').exists())
