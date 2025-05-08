from datetime import datetime

from django.contrib.auth.hashers import check_password
from django.db import models


# Create your models here.
class User(models.Model):
    account = models.CharField(max_length=50)
    password = models.CharField(max_length=300)
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(null=True)
    address = models.TextField(max_length=1000)
    name=models.CharField(max_length=100)
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'user'
