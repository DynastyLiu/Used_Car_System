# -*- coding: utf-8 -*-
"""
管理员审核模块视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle

from .models import VehicleReview, UserAuthenticationReview, SystemReport, AdminOperationLog
from .serializers import (
    VehicleReviewSerializer, UserAuthenticationReviewSerializer, SystemReportSerializer,
    AdminOperationLogSerializer, AdminDashboardSerializer,
    VehicleReviewActionSerializer, UserAuthenticationReviewActionSerializer,
    SystemReportActionSerializer
)

User = get_user_model()


def has_admin_permission(user):
    """检查用户是否有管理员权限"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


class BaseAdminViewSet(viewsets.ModelViewSet):
    """管理员基础ViewSet"""
    permission_classes = [IsAdminUser]

    def initial(self, request, *args, **kwargs):
        """初始化时检查权限"""
        super().initial(request, *args, **kwargs)
        if not has_admin_permission(request.user):
            self.permission_denied(
                request,
                message='需要管理员权限才能访问此功能'
            )

    def log_admin_operation(self, operation_type, target_type, target_id, description):
        """记录管理员操作日志"""
        AdminOperationLog.objects.create(
            admin=self.request.user,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def get_client_ip(self):
        """获取客户端IP"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class VehicleReviewViewSet(BaseAdminViewSet):
    """
    车辆审核管理ViewSet
    """
    queryset = VehicleReview.objects.select_related('vehicle', 'reviewer').all()
    serializer_class = VehicleReviewSerializer

    def get_queryset(self):
        """根据状态过滤"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        处理车辆审核
        POST /api/admin/vehicle-reviews/{id}/process/
        """
        review = self.get_object()

        if review.status != 'pending':
            return Response(
                {'error': '该审核已处理，无法重复操作'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VehicleReviewActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']
        review_note = serializer.validated_data.get('review_note', '')

        # 更新审核记录
        review.status = 'approved' if action == 'approve' else 'rejected'
        review.reviewer = request.user
        review.review_note = review_note
        review.review_time = timezone.now()
        review.save()

        # 更新车辆状态
        vehicle = review.vehicle
        if action == 'approve':
            vehicle.review_status = 'approved'
            vehicle.status = 'listed'
            operation_desc = f"审核通过车辆: {vehicle.brand.name} {vehicle.model_name}"
        else:
            vehicle.review_status = 'rejected'
            vehicle.status = 'rejected'
            operation_desc = f"审核拒绝车辆: {vehicle.brand.name} {vehicle.model_name} - {review_note}"

        vehicle.save(update_fields=['review_status', 'status'])

        # 记录操作日志
        self.log_admin_operation(
            operation_type=f'vehicle_{action}',
            target_type='vehicle',
            target_id=vehicle.id,
            description=operation_desc
        )

        return Response({
            'message': f'车辆审核{review.get_status_display()}',
            'status': review.status
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取审核统计信息
        GET /api/admin/vehicle-reviews/statistics/
        """
        stats = VehicleReview.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            approved=Count('id', filter=Q(status='approved')),
            rejected=Count('id', filter=Q(status='rejected'))
        )

        return Response(stats)


class UserAuthenticationReviewViewSet(BaseAdminViewSet):
    """
    用户实名认证审核管理ViewSet
    """
    queryset = UserAuthenticationReview.objects.select_related('user', 'reviewer').all()
    serializer_class = UserAuthenticationReviewSerializer

    def get_queryset(self):
        """根据状态过滤"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        处理用户认证审核
        POST /api/admin/user-auth-reviews/{id}/process/
        """
        review = self.get_object()

        if review.status != 'pending':
            return Response(
                {'error': '该认证已审核，无法重复操作'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserAuthenticationReviewActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']
        review_note = serializer.validated_data.get('review_note', '')

        # 更新审核记录
        review.status = 'approved' if action == 'approve' else 'rejected'
        review.reviewer = request.user
        review.review_note = review_note
        review.review_time = timezone.now()

        # 保存快照数据
        user = review.user
        review.id_number_snapshot = user.id_number
        review.id_front_image_snapshot = user.id_front_image
        review.id_back_image_snapshot = user.id_back_image
        review.save()

        # 更新用户认证状态
        if action == 'approve':
            user.real_name_auth_status = 'verified'
            operation_desc = f"审核通过用户认证: {user.username}"
        else:
            user.real_name_auth_status = 'rejected'
            operation_desc = f"审核拒绝用户认证: {user.username} - {review_note}"

        user.save(update_fields=['real_name_auth_status'])

        # 记录操作日志
        self.log_admin_operation(
            operation_type=f'user_auth_{action}',
            target_type='user',
            target_id=user.id,
            description=operation_desc
        )

        return Response({
            'message': f'用户认证{review.get_status_display()}',
            'status': review.status
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取认证审核统计信息
        GET /api/admin/user-auth-reviews/statistics/
        """
        stats = UserAuthenticationReview.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            approved=Count('id', filter=Q(status='approved')),
            rejected=Count('id', filter=Q(status='rejected'))
        )

        return Response(stats)


class SystemReportViewSet(BaseAdminViewSet):
    """
    系统举报管理ViewSet
    """
    queryset = SystemReport.objects.select_related(
        'reporter', 'reported_user', 'reported_vehicle', 'handler'
    ).all()
    serializer_class = SystemReportSerializer

    def get_queryset(self):
        """根据状态和类型过滤"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        type_filter = self.request.query_params.get('type')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if type_filter:
            queryset = queryset.filter(report_type=type_filter)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        处理举报
        POST /api/admin/system-reports/{id}/process/
        """
        report = self.get_object()

        if report.status in ['resolved', 'dismissed']:
            return Response(
                {'error': '该举报已处理完成'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SystemReportActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']
        handling_note = serializer.validated_data.get('handling_note', '')

        # 更新举报状态
        report.status = action
        report.handler = request.user
        report.handling_note = handling_note

        if action in ['resolved', 'dismissed']:
            report.resolved_at = timezone.now()

        report.save()

        # 记录操作日志
        self.log_admin_operation(
            operation_type='report_handle',
            target_type='report',
            target_id=report.id,
            description=f"处理举报: {report.title} - {report.get_status_display()}"
        )

        return Response({
            'message': f'举报{report.get_status_display()}',
            'status': report.status
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取举报统计信息
        GET /api/admin/system-reports/statistics/
        """
        stats = SystemReport.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            processing=Count('id', filter=Q(status='processing')),
            resolved=Count('id', filter=Q(status='resolved')),
            dismissed=Count('id', filter=Q(status='dismissed'))
        )

        # 按类型统计
        type_stats = SystemReport.objects.values('report_type').annotate(
            count=Count('id')
        ).order_by('-count')

        return Response({
            'overall': stats,
            'by_type': list(type_stats)
        })


class AdminDashboardViewSet(BaseAdminViewSet):
    """
    管理员仪表板ViewSet
    """
    queryset = VehicleReview.objects.none()  # 不需要默认查询集

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        获取仪表板数据
        GET /api/admin/dashboard/
        """
        # 统计数据
        now = timezone.now()
        today = now.date()

        stats = {
            # 待审核数量
            'pending_vehicle_reviews': VehicleReview.objects.filter(status='pending').count(),
            'pending_user_auth_reviews': UserAuthenticationReview.objects.filter(status='pending').count(),
            'pending_reports': SystemReport.objects.filter(status='pending').count(),

            # 总数统计
            'total_users': User.objects.count(),
            'total_vehicles': Vehicle.objects.count(),

            # 今日新增
            'today_new_users': User.objects.filter(date_joined__date=today).count(),
            'today_new_vehicles': Vehicle.objects.filter(created_at__date=today).count(),
        }

        # 最近活动
        recent_reviews = VehicleReview.objects.order_by('-created_at')[:5]
        recent_auth_reviews = UserAuthenticationReview.objects.order_by('-created_at')[:5]
        recent_reports = SystemReport.objects.order_by('-created_at')[:5]
        recent_operations = AdminOperationLog.objects.order_by('-created_at')[:10]

        data = {
            **stats,
            'recent_reviews': VehicleReviewSerializer(recent_reviews, many=True).data,
            'recent_auth_reviews': UserAuthenticationReviewSerializer(recent_auth_reviews, many=True).data,
            'recent_reports': SystemReportSerializer(recent_reports, many=True).data,
            'recent_operations': AdminOperationLogSerializer(recent_operations, many=True).data,
        }

        return Response(data)

    @action(detail=False, methods=['get'])
    def operation_logs(self, request):
        """
        获取操作日志
        GET /api/admin/operation-logs/
        """
        queryset = AdminOperationLog.objects.select_related('admin').order_by('-created_at')

        # 过滤参数
        admin_id = request.query_params.get('admin')
        operation_type = request.query_params.get('operation_type')
        target_type = request.query_params.get('target_type')

        if admin_id:
            queryset = queryset.filter(admin_id=admin_id)
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        if target_type:
            queryset = queryset.filter(target_type=target_type)

        # 分页
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        items = queryset[start:end]

        return Response({
            'items': AdminOperationLogSerializer(items, many=True).data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })


# ============ 管理员页面视图 ============
def admin_dashboard_view(request):
    """
    管理员仪表板页面
    """
    return render(request, 'admin/dashboard.html')


def admin_vehicle_reviews_view(request):
    """
    车辆审核页面
    """
    return render(request, 'admin/vehicle_reviews.html')


def admin_user_auth_reviews_view(request):
    """
    用户认证审核页面
    """
    return render(request, 'admin/user_auth_reviews.html')


def admin_reports_view(request):
    """
    举报管理页面
    """
    return render(request, 'admin/reports.html')


def admin_operation_logs_view(request):
    """
    操作日志页面
    """
    return render(request, 'admin/operation_logs.html')
