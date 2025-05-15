# gateway/user/serializers.py

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class UserRequestSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ['user_id', 'account', 'password', 'age', 'gender', 'created_at', 'address', 'name']
        read_only_fields = ['user_id', 'created_at']

    def create(self, validated_data):
        user = User(
            account=validated_data['account'],
            age=validated_data.get('age', 0),
            gender=validated_data.get('gender', ''),
            password=make_password(validated_data['password']),
            address=validated_data.get('address', ''),
            name=validated_data.get('name')  # name 없어도 None 저장
        )
        user.save()
        return user

class LoginSerializer(serializers.ModelSerializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['account', 'password']

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
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': str(user.user_id),  # 반환에 user_id 포함!
            'account': user.account,
        }

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'account', 'age', 'gender', 'created_at', 'address', 'name']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['account']
