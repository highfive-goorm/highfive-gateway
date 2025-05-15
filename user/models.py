# gateway/user/models.py

import uuid
from django.db import models
from django.contrib.auth.hashers import check_password

class User(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    account = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=300)
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(max_length=1000)
    name = models.CharField(max_length=100, blank=True, null=True)   # name은 Optional

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'user'
