# gateway/user/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserView, LoginView, UserCheckView

urlpatterns = [
    path('', UserView.as_view()),  # POST (회원가입)
    path('/<uuid:user_id>', UserView.as_view()),  # GET/PUT/DELETE
    path('/login', LoginView.as_view(), name='login'),
    path('/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('/check-duplicate', UserCheckView.as_view())
]
