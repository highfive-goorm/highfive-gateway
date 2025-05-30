# gateway/user/models.py
import hashlib
import uuid
from django.db import models
from django.contrib.auth.hashers import check_password
from django.utils.crypto import get_random_string


class User(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    account = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=300)
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(max_length=1000)
    name = models.CharField(max_length=100, blank=True, null=True)  # name은 Optional

    REQUIRED_FIELDS = []

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    USERNAME_FIELD = 'account'

    @property
    def is_active(self):
        # status가 1 이상이면 활성 사용자로 간주
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_unusable_password(self):
        # Django와 호환되는 unusable hash 값
        self.password = f"!{hashlib.sha256(get_random_string(32).encode()).hexdigest()}"
    class Meta:
        db_table = 'user'
