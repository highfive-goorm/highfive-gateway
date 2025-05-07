from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import LoginSerializer
from .user_service import create_user



class UserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):  #회원 가입
        account=request.GET.get('account')
        is_duplicate = User.objects.filter(account=account).exists()


        if not is_duplicate:
            user = create_user(request.data, current_user=None)
            return Response(user, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "중복 됩니다."},status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
