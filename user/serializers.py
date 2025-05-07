from rest_framework import serializers

from django.contrib.auth.hashers import make_password
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['account', 'password', 'age', 'gender']

    def create(self, validated_data):
        user = User(
            account=validated_data['account'],
            age=validated_data['age'],
            gender=validated_data['gender'],
            password=make_password(validated_data['password'],
                                   )
        )
        user.save()
        return user


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account', 'age', 'gender', 'created_at']


class UserPutResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account', 'age', 'gender', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        account = attrs.get('account')
        password = attrs.get('password')
        try:
            user = User.objects.get(account=account)
        except User.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 계정입니다.")

        if not user.check_password(password):
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }