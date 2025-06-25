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
from django_prometheus import exports
from . import views
from .views import AdminView, ProductProxyView, OrderProxyView, CartProxyView, AlertProxyView, RecommendProxyView, \
    LikeProxyView, BrandLikeProxyView, TrackingProxyView, PromotionProxyView

urlpatterns = [
    path('test-error/', views.test_exception_view, name='test_exception_view'),
    path("metrics", exports.ExportToDjangoView, name="prometheus-django-metrics"),
    path('product', ProductProxyView.as_view(), name='product-list-create'),
    path('product/<int:id>', ProductProxyView.as_view(), name='product-detail'),
    path('product/like/count/<str:user_id>', LikeProxyView.as_view(), name='product-like-count'),
    path('product/<int:id>/like', LikeProxyView.as_view(), name='product-like-create'),
    path('product/<int:id>/like/<str:user_id>', LikeProxyView.as_view(), name='product-like-delete'),
    path('brand/like/count/<str:user_id>', BrandLikeProxyView.as_view(), name='brand-like-count'),
    path('brand/<int:id>/like', BrandLikeProxyView.as_view(), name='brand-like-create'),
    path('brand/<int:id>/like/<str:user_id>', BrandLikeProxyView.as_view(), name='brand-like-delete'),
    path('admin', AdminView.as_view(), name='admin-proxy'),
    path('user', include('user.urls')),
    path('order', OrderProxyView.as_view(), name='order-create'),
    path('order/<str:id>', OrderProxyView.as_view(), name='order-detail-manage'),
    path('order/user/<str:user_id>', OrderProxyView.as_view(), name='order-list-by-user'),
    path('cart/<str:user_id>', CartProxyView.as_view(), name='cart-detail'),
    path('cart/<str:user_id>/<str:product_id>', CartProxyView.as_view(), name='cart-item-manage'),
    path('alert', AlertProxyView.as_view(), name='alert-list-create'),
    path('alert/<int:id>', AlertProxyView.as_view(), name='alert-detail-manage'),
    path('recommend/<str:user_id>', RecommendProxyView.as_view(), name='recommend-for-user'),
    path('ht/', include('health_check.urls')),
    # Tracking Service
    path('tracking/log/event', TrackingProxyView.as_view(), name='tracking_log_event'),
    # Promotion Service (Simplified URLs)
    path('promotion/active', PromotionProxyView.as_view(), {'action': 'active'}, name='promotion_active_list'),  # GET
    path('promotion', PromotionProxyView.as_view(), name='promotion_create'),  # POST
    path('promotion/<str:promotion_id>', PromotionProxyView.as_view(), name='promotion_detail_manage'),  # GET, PATCH, DELETE
    # KakaoPay Order Endpoints
    path('payment/kakao/ready', OrderProxyView.as_view(), name='kakao_payment_ready'), # POST
    path('payment/kakao/approve', OrderProxyView.as_view(), name='kakao_payment_approve'), # POST
]
