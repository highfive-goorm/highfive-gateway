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
from django.contrib import admin
from django.urls import path, include, re_path

from .views import AdminView, ProductProxyView, OrderProxyView, CartProxyView, AlertProxyView, RecommendProxyView, \
    LikeProxyView, BrandLikeProxyView

urlpatterns = [  # POST /product, GET /product?name=
    path('product', ProductProxyView.as_view()),
    path('product/<int:id>', ProductProxyView.as_view()),
    path('product/like/count/<str:user_id>', LikeProxyView.as_view()),
    path('product/<int:id>/like', LikeProxyView.as_view()),
    path('product/<int:id>/like/<str:user_id>', LikeProxyView.as_view()),
    path('brand/like/count/<str:user_id>', BrandLikeProxyView.as_view()),
    path('brand/<int:id>/like', BrandLikeProxyView.as_view()),
    path('brand/<int:id>/like/<str:user_id>', BrandLikeProxyView.as_view()),
    path('admin', AdminView.as_view()),
    path('user', include('user.urls')),
    path('order', OrderProxyView.as_view()),
    path('order/<str:user_id>',OrderProxyView.as_view()),
    path('cart', CartProxyView.as_view()),
    path('cart/<str:user_id>', CartProxyView.as_view()),
    path('cart/<str:user_id>/<str:product_id>', CartProxyView.as_view()),
    path('alert', AlertProxyView.as_view()),
    path('alert/<int:id>', AlertProxyView.as_view()),
    path('recommend/<str:user_id>', RecommendProxyView.as_view()),
    path('ht/', include('health_check.urls')),
]
