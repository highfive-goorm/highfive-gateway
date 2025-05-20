# gateway/user/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
User = get_user_model()
from .serializers import LoginSerializer, UserResponseSerializer, AccountSerializer, UserRequestSerializer


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
            # DRF가 각 클래스에 대해 인스턴스를 생성하도록 합니다.
        return [permission() for permission in perms]

    # POST /user/ (회원가입)
    def post(self, request):
        if User.objects.filter(account=request.data['account']).exists():
            return Response({"message": "중복 됩니다."}, status=status.HTTP_400_BAD_REQUEST)
        user = create_user(request.data)
        serializer = UserResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /user/<uuid:user_id> (조회)
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            serializer = UserResponseSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # PUT /user/<uuid:user_id> (수정)
    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserResponseSerializer(user, data=request.data, partial=True)
        if request.data['password']=='':
            return Response({"message": "비밀번호 공란은 안됩니다"}, status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /user/<uuid:user_id> (삭제)
    def delete(self, request, user_id):
        try:
            user = get_object_or_404(User, user_id=user_id)
            user.account = f"deleted_{user.user_id}"
            user.set_unusable_password()
            user.save()
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

        return Response({"exists": not serializer.is_valid()})
