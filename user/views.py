from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import LoginSerializer, UserResponseSerializer, AccountSerializer
from .user_service import create_user


class UserResponse:
    def __init__(self, account, age, gender, address, created_at, name):
        self.account = account
        self.age = age
        self.gender = gender
        self.address = gender
        self.address = address
        self.created_at = created_at
        self.name = name


class UserView(APIView):
    permission_classes = [AllowAny]

    # ✅ POST: 회원 가입
    def post(self, request):
        if not User.objects.filter(account=request.data['account']).exists():
            user = create_user(request.data, current_user=None)
            serializer = UserResponseSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "중복 됩니다."}, status=status.HTTP_400_BAD_REQUEST)

    #     # ✅ GET: 사용자 정보 조회 (id 기준)
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            serializer = UserResponseSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # ✅ PUT: 사용자 정보 수정 (id 기준)
    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserResponseSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ DELETE: 사용자 삭제 (id 기준)
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.delete()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AccountSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        account = serializer.validated_data.get('account')

        # account 중복 여부 확인
        if User.objects.filter(account=account).exists():
            return Response({"exists": True}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({"exists": False}, status=status.HTTP_200_OK)
