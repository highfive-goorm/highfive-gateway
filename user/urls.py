"""
URL configuration for highfive_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import UserView, LoginView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),  # 로그인
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),  # access 토큰 갱신
    path('', UserView.as_view()),  #회원가입
]
