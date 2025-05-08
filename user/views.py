from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import LoginSerializer, UserResponseSerializer
from .user_service import create_user


class UserResponse:
    def __init__(self,account,age,gender,address,created_at,name):

        self.account=account
        self.age = age
        self.gender=gender
        self.address=gender
        self.address = address
        self.created_at = created_at
        self.name=name


class UserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):  #회원 가입

        if not User.objects.filter(account=request.data['account']).exists():
            user = create_user(request.data, current_user=None)
            serializer = UserResponseSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "중복 됩니다."}, status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
