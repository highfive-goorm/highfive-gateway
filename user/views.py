from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
User = get_user_model()

from .serializers import (
    UserRequestSerializer,
    UserResponseSerializer,
    LoginSerializer,
    AccountSerializer,
)

import logging
logger = logging.getLogger()  # settings.py 에서 붙여둔 핸들러(파일+콘솔)를 그대로 사용합니다.

def create_user(data):
    serializer = UserRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return user


class UserView(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            perms = [AllowAny]
        else:
            perms = [IsAuthenticated]
        return [permission() for permission in perms]

    # POST /user/ (회원가입)
    def post(self, request):
        # 회원가입 시도 로그
        logger.info(f"create_user_start\taccount={request.data.get('account','')}")
        if User.objects.filter(account=request.data.get('account', '')).exists():
            logger.warning(f"create_user_failed\treason=duplicate_account\taccount={request.data.get('account','')}")
            return Response(
                {"message": "중복 됩니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = create_user(request.data)
        logger.info(f"create_user_success\tuser_id={user.user_id}\taccount={user.account}")

        serializer = UserResponseSerializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    # GET /user/<uuid:user_id> (조회)
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            serializer = UserResponseSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

    # PUT /user/<uuid:user_id> (수정)
    def put(self, request, user_id):
        # 수정 시도 로그
        logger.info(f"update_user_start\tuser_id={user_id}\tupdate_fields={list(request.data.keys())}")

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            logger.error(f"update_user_failed\treason=not_found\tuser_id={user_id}")
            return Response(
                {"message": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        # 빈 비밀번호 필드 제외
        if data.get('password', '') == '':
            data.pop('password')

        serializer = UserResponseSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"update_user_success\tuser_id={user_id}\tchanged_fields={list(data.keys())}")
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        logger.error(f"update_user_failed\terrors={serializer.errors}\tuser_id={user_id}")
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # DELETE /user/<uuid:user_id> (삭제)
    def delete(self, request, user_id):
        try:
            user = get_object_or_404(User, user_id=user_id)
            user.account = f"deleted_{user.user_id}"
            user.set_unusable_password()
            user.save()
            return Response(
                {"message": "삭제되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    # POST /login/ (로그인)
    def post(self, request):
        # 로그인 시도 로그
        logger.info(f"login_start\taccount={request.data.get('account','')}")
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 로그인 성공 로그
        logger.info(f"login_success\tuser_id={serializer.validated_data.get('user_id')}")
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class UserCheckView(APIView):
    permission_classes = [AllowAny]

    # POST /user/check/ (계정 중복 확인)
    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        return Response(
            {"exists": not serializer.is_valid()},
            status=status.HTTP_200_OK,
        )
