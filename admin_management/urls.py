"""
管理员审核模块URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vehicle-reviews', views.VehicleReviewViewSet, basename='admin_vehicle_review')
router.register(r'user-auth-reviews', views.UserAuthenticationReviewViewSet, basename='admin_user_auth_review')
router.register(r'system-reports', views.SystemReportViewSet, basename='admin_system_report')
router.register(r'dashboard', views.AdminDashboardViewSet, basename='admin_dashboard')

urlpatterns = [
    # API路由
    path('', include(router.urls)),
]