#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卖家中心API路由配置
"""
import sys
import os

# 添加项目根目录到Python路径，以便正确导入seller_views
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from orders.models import Order
from vehicles.models import Vehicle
from vehicles.views import VehicleViewSet

# 导入seller_views中的ViewSet
try:
    from seller_views import (
        SellerOrderViewSet,
        SellerPricingViewSet,
        SellerReviewViewSet,
        SellerAnalyticsViewSet,
    )
except ImportError as e:
    print(f"警告：无法导入seller_views: {e}")
    print("请确保seller_views.py文件在项目根目录中")
    raise

# 卖家统计API
class SellerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取卖家统计数据"""
        user = request.user

        # 获取统计数据
        vehicles = Vehicle.objects.filter(seller=user)
        orders = Order.objects.filter(seller=user)

        total_vehicles = vehicles.filter(status__in=['listed', 'pending_review', 'sold']).count()
        sold_vehicles = vehicles.filter(status='sold').count()
        pending_orders = orders.filter(status__in=['pending_payment', 'paid']).count()

        # 计算总收入（已完成订单）
        total_revenue = orders.filter(status='completed').aggregate(
            total=Sum('price')
        )['total'] or 0

        return Response({
            'total_vehicles': total_vehicles,
            'sold_vehicles': sold_vehicles,
            'pending_orders': pending_orders,
            'total_revenue': float(total_revenue),
        })

router = DefaultRouter()

# 订单管理
router.register(r'orders', SellerOrderViewSet, basename='seller-orders')

# 定价管理
router.register(r'pricing', SellerPricingViewSet, basename='seller-pricing')

# 评价管理
router.register(r'reviews', SellerReviewViewSet, basename='seller-reviews')

# 数据分析
router.register(r'analytics', SellerAnalyticsViewSet, basename='seller-analytics')

# 车辆管理
router.register(r'vehicles', VehicleViewSet, basename='seller-vehicles')

urlpatterns = [
    path('stats/', SellerStatsView.as_view(), name='seller-stats'),
    path('', include(router.urls)),
]
