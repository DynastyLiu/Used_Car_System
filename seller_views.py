#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卖家中心API视图
包含订单管理、定价管理、评价管理、统计分析等功能
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db.models import Q, Count, Avg, Sum, F, Prefetch
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import json

from users.models import User
from orders.models import Order, OrderReview, OrderPayment
from vehicles.models import Vehicle, VehiclePrice, VehiclePriceHistory, CarBrand
from seller_serializers import (
    SellerOrderSerializer,
    VehiclePriceSerializer,
    VehiclePriceHistorySerializer,
    SellerReviewSerializer,
    SellerAnalyticsSerializer
)


class BaseSellerViewSet(viewsets.ModelViewSet):
    """卖家中心基类ViewSet"""
    permission_classes = [permissions.IsAuthenticated]


class SellerOrderViewSet(viewsets.ModelViewSet):
    """
    卖家订单管理ViewSet
    - GET /api/seller/orders/ - 获取订单列表
    - POST /api/seller/orders/{id}/confirm/ - 确认订单
    - POST /api/seller/orders/{id}/cancel/ - 取消订单
    - POST /api/seller/orders/{id}/complete/ - 完成订单
    - GET /api/seller/orders/export/ - 导出订单
    """
    serializer_class = SellerOrderSerializer
    queryset = Order.objects.all().select_related('buyer', 'vehicle', 'payment')
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(seller=self.request.user).select_related('buyer', 'vehicle', 'payment')

        # 状态筛选
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 时间筛选
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """获取订单列表，包含统计信息"""
        queryset = self.filter_queryset(self.get_queryset())

        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            # 计算统计数据
            stats = self.get_order_stats()

            return self.get_paginated_response({
                'results': serializer.data,
                'stats': stats
            })

        serializer = self.get_serializer(queryset, many=True)
        stats = self.get_order_stats()

        return Response({
            'results': serializer.data,
            'stats': stats
        })

    def get_order_stats(self):
        """获取订单统计数据"""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending_payment').count(),
            'confirmed': queryset.filter(status='paid').count(),
            'completed': queryset.filter(status='completed').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
            'total_revenue': queryset.filter(status='completed').aggregate(
                total=Sum('price')
            )['total'] or 0
        }

        return stats

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认订单"""
        order = self.get_object()

        if order.status != 'pending_payment':
            return Response(
                {'error': '只能确认待付款的订单'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()

        # 记录操作日志
        self.log_operation(order, 'confirm', '确认订单')

        return Response({'message': '订单确认成功'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        reason = request.data.get('reason', '')

        if order.status in ['completed', 'cancelled']:
            return Response(
                {'error': '该订单无法取消'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.seller_note = reason
        order.save()

        # 记录操作日志
        self.log_operation(order, 'cancel', f'取消订单: {reason}')

        return Response({'message': '订单取消成功'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成订单"""
        order = self.get_object()

        if order.status != 'paid':
            return Response(
                {'error': '只能完成已付款的订单'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()

        # 更新车辆状态为已售
        if order.vehicle:
            order.vehicle.status = 'sold'
            order.vehicle.sold_at = timezone.now()
            order.vehicle.save()

        # 记录操作日志
        self.log_operation(order, 'complete', '完成订单')

        return Response({'message': '订单完成成功'})

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出订单数据为CSV"""
        queryset = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            '订单号', '买家', '车辆', '价格', '状态', '创建时间', '付款时间', '完成时间'
        ])

        for order in queryset:
            writer.writerow([
                order.order_number,
                order.buyer.username if order.buyer else '',
                order.vehicle.model_name if order.vehicle else '',
                order.price,
                order.get_status_display(),
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.paid_at.strftime('%Y-%m-%d %H:%M:%S') if order.paid_at else '',
                order.completed_at.strftime('%Y-%m-%d %H:%M:%S') if order.completed_at else ''
            ])

        return response

    def log_operation(self, order, action, description):
        """记录操作日志"""
        from users.models import UserOperationLog

        UserOperationLog.objects.create(
            user=self.request.user,
            operation_type=f'order_{action}',
            description=f'订单#{order.id}: {description}',
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
        )

    def get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SellerPricingViewSet(viewsets.ModelViewSet):
    """
    卖家定价管理ViewSet
    - GET /api/seller/pricing/ - 获取价格列表
    - GET /api/seller/pricing/{id}/ - 获取价格详情
    - PUT /api/seller/pricing/{id}/ - 更新价格
    - GET /api/seller/pricing/{id}/history/ - 获取价格历史
    - GET /api/seller/ai-pricing/{vehicle_id}/ - 获取AI定价建议
    """
    serializer_class = VehiclePriceSerializer
    queryset = VehiclePrice.objects.all().select_related('vehicle')
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 只返回当前卖家车辆的价格信息
        return VehiclePrice.objects.filter(vehicle__seller=self.request.user).select_related('vehicle').order_by('-updated_at')

    @action(detail=False, methods=['get'], url_path='ai-pricing/(?P<vehicle_id>[^/.]+)')
    def ai_pricing(self, request, vehicle_id=None):
        """获取AI智能定价建议"""
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id, seller=request.user)
        except Vehicle.DoesNotExist:
            return Response(
                {'error': '车辆不存在或无权限'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 模拟AI定价建议（实际应该调用AI服务）
        suggested_price = self.calculate_ai_price(vehicle)

        return Response({
            'vehicle_id': vehicle.id,
            'vehicle_name': f'{vehicle.brand.name} {vehicle.model_name}',
            'recommended_price': suggested_price['price'],
            'min_price': suggested_price['min_price'],
            'max_price': suggested_price['max_price'],
            'confidence': suggested_price['confidence'],
            'reason': suggested_price['reason']
        })

    def calculate_ai_price(self, vehicle):
        """计算AI定价建议（简化版本）"""
        base_price = float(vehicle.price)

        # 根据车龄调整价格
        current_year = timezone.now().year
        vehicle_age = current_year - vehicle.year
        age_factor = max(0.3, 1 - (vehicle_age * 0.1))

        # 根据里程调整价格
        mileage_factor = max(0.5, 1 - (vehicle.mileage / 200000))

        # 根据品牌调整价格
        brand_factor = 1.0
        if vehicle.brand.country == 'import':
            brand_factor = 1.2

        # 计算最终价格
        suggested_price = base_price * age_factor * mileage_factor * brand_factor

        return {
            'price': round(suggested_price, 2),
            'min_price': round(suggested_price * 0.9, 2),
            'max_price': round(suggested_price * 1.1, 2),
            'confidence': 0.85,
            'reason': f'基于{vehicle.year}年款、里程{vehicle.mileage}km、{vehicle.brand.name}品牌等因素计算'
        }

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """获取价格变化历史"""
        pricing = self.get_object()
        history = VehiclePriceHistory.objects.filter(
            vehicle=pricing.vehicle
        ).order_by('-changed_at')

        serializer = VehiclePriceHistorySerializer(history, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """更新价格信息"""
        pricing = self.get_object()

        # 记录价格变化历史
        old_price = pricing.suggested_price
        new_price = request.data.get('suggested_price')

        if new_price and old_price != float(new_price):
            VehiclePriceHistory.objects.create(
                vehicle=pricing.vehicle,
                old_price=old_price,
                new_price=new_price,
                change_reason=request.data.get('change_reason', '手动调整')
            )

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def update_vehicle_price(self, request, pk=None):
        """更新车辆的实际售价

        POST /api/seller/pricing/{id}/update_vehicle_price/
        {
            "new_price": 250000,
            "change_reason": "市场竞争调整"
        }
        """
        try:
            pricing = self.get_object()
            vehicle = pricing.vehicle

            # 验证权限
            if vehicle.seller != request.user:
                return Response(
                    {'error': '无权限修改此车辆价格'},
                    status=status.HTTP_403_FORBIDDEN
                )

            new_price = request.data.get('new_price')
            change_reason = request.data.get('change_reason', '手动调整价格')

            if not new_price:
                return Response(
                    {'error': '新价格不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                new_price = float(new_price)
                if new_price <= 0:
                    raise ValueError("价格必须大于0")
            except (ValueError, TypeError):
                return Response(
                    {'error': '价格格式不正确，必须是大于0的数字'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_price = float(vehicle.price)

            # 如果价格没有变化，直接返回
            if old_price == new_price:
                return Response({
                    'message': '价格没有变化',
                    'vehicle_id': vehicle.id,
                    'current_price': old_price
                })

            # 更新车辆价格
            vehicle.price = new_price
            vehicle.save(update_fields=['price', 'updated_at'])

            # 记录价格变化历史
            VehiclePriceHistory.objects.create(
                vehicle=vehicle,
                old_price=old_price,
                new_price=new_price,
                change_reason=change_reason
            )

            # 同时更新VehiclePrice表中的建议价格（如果需要）
            if pricing.suggested_price != new_price:
                pricing.suggested_price = new_price
                pricing.save(update_fields=['suggested_price', 'updated_at'])

            return Response({
                'message': '价格更新成功',
                'vehicle_id': vehicle.id,
                'old_price': old_price,
                'new_price': new_price,
                'change_reason': change_reason,
                'updated_at': vehicle.updated_at.isoformat()
            })

        except Exception as e:
            return Response(
                {'error': f'价格更新失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SellerReviewViewSet(viewsets.ModelViewSet):
    """
    卖家评价管理ViewSet
    - GET /api/seller/reviews/ - 获取评价列表
    - POST /api/seller/reviews/{id}/reply/ - 回复评价
    - GET /api/seller/reviews/stats/ - 获取评价统计
    """
    serializer_class = SellerReviewSerializer
    queryset = OrderReview.objects.all().select_related('order', 'reviewer', 'order__vehicle')
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 只返回当前卖家收到的评价
        return OrderReview.objects.filter(order__seller=self.request.user).select_related('order', 'reviewer', 'order__vehicle')

    def list(self, request, *args, **kwargs):
        """获取评价列表，包含统计信息"""
        queryset = self.filter_queryset(self.get_queryset())

        # 评分筛选
        rating_filter = self.request.query_params.get('rating', '')
        if rating_filter:
            queryset = queryset.filter(rating=rating_filter)

        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            # 计算统计数据
            stats = self.get_review_stats()

            return self.get_paginated_response({
                'results': serializer.data,
                'stats': stats
            })

        serializer = self.get_serializer(queryset, many=True)
        stats = self.get_review_stats()

        return Response({
            'results': serializer.data,
            'stats': stats
        })

    def get_review_stats(self):
        """获取评价统计数据"""
        queryset = self.get_queryset()

        # 基础统计
        total_reviews = queryset.count()

        if total_reviews == 0:
            return {
                'total': 0,
                'average_rating': 0,
                'rating_distribution': {},
                'response_rate': 0,
                'recent': 0
            }

        # 平均评分
        avg_rating = queryset.aggregate(avg=Avg('rating'))['avg'] or 0

        # 评分分布
        rating_dist = {}
        for i in range(1, 6):
            count = queryset.filter(rating=i).count()
            rating_dist[str(i)] = count

        # 回复率（检查订单的seller_note是否包含回复内容）
        replied_count = queryset.exclude(order__seller_note__isnull=True).exclude(order__seller_note='').count()
        response_rate = (replied_count / total_reviews * 100) if total_reviews > 0 else 0

        # 最近30天评价数
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_count = queryset.filter(created_at__gte=thirty_days_ago).count()

        return {
            'total': total_reviews,
            'average_rating': round(avg_rating, 1),
            'rating_distribution': rating_dist,
            'response_rate': round(response_rate, 1),
            'recent': recent_count
        }

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """回复评价"""
        review = self.get_object()
        reply_content = request.data.get('reply', '')

        if not reply_content.strip():
            return Response(
                {'error': '回复内容不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 将回复内容存储在订单的seller_note字段中
        # 注意：这是一个简化的实现，实际应该有专门的回复模型
        if review.order.seller_note:
            review.order.seller_note += f"\n\n回复评价#{review.id}: {reply_content}"
        else:
            review.order.seller_note = f"回复评价#{review.id}: {reply_content}"
        review.order.save()

        return Response({'message': '回复成功'})


class SellerAnalyticsViewSet(viewsets.ViewSet):
    """
    卖家统计分析ViewSet
    - GET /api/seller/analytics/ - 获取分析数据
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """获取统计分析数据"""
        period = request.query_params.get('period', '30d')

        # 根据周期计算时间范围
        end_date = timezone.now()
        if period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)

        # 获取数据
        analytics_data = self.calculate_analytics(request.user, start_date, end_date)

        return Response(analytics_data)

    def calculate_analytics(self, seller, start_date, end_date):
        """计算分析数据"""

        # 1. KPI指标
        orders = Order.objects.filter(
            seller=seller,
            created_at__range=[start_date, end_date]
        )

        completed_orders = orders.filter(status='completed')

        total_revenue = completed_orders.aggregate(total=Sum('price'))['total'] or 0
        total_orders = orders.count()
        avg_price = completed_orders.aggregate(avg=Avg('price'))['avg'] or 0

        # 计算转化率（浏览量转订单数）
        seller_vehicles = Vehicle.objects.filter(seller=seller)
        total_views = seller_vehicles.aggregate(total=Sum('view_count'))['total'] or 1
        conversion_rate = (total_orders / total_views * 100) if total_views > 0 else 0

        # 2. 计算趋势（与上一周期对比）
        previous_start = start_date - (end_date - start_date)
        previous_end = start_date

        previous_orders = Order.objects.filter(
            seller=seller,
            created_at__range=[previous_start, previous_end]
        )
        previous_completed = previous_orders.filter(status='completed')
        previous_revenue = previous_completed.aggregate(total=Sum('price'))['total'] or 0
        previous_order_count = previous_orders.count()

        # 趋势计算
        revenue_trend = self.calculate_trend(previous_revenue, total_revenue)
        orders_trend = self.calculate_trend(previous_order_count, total_orders)
        price_trend = self.calculate_trend(
            previous_completed.aggregate(avg=Avg('price'))['avg'] or 0,
            avg_price
        )
        conversion_trend = 0  # 简化处理

        kpis = {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'avg_price': float(avg_price),
            'conversion_rate': round(conversion_rate, 2),
            'revenue_trend': revenue_trend,
            'orders_trend': orders_trend,
            'price_trend': price_trend,
            'conversion_trend': conversion_trend
        }

        # 3. 图表数据
        charts = self.generate_charts(seller, start_date, end_date)

        return {
            'kpis': kpis,
            'charts': charts,
            'period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        }

    def calculate_trend(self, previous, current):
        """计算趋势百分比"""
        if previous == 0:
            return 100 if current > 0 else 0

        return round((current - previous) / previous * 100, 1)

    def generate_charts(self, seller, start_date, end_date):
        """生成图表数据"""

        # 销售趋势图
        sales_trend = self.generate_sales_trend(seller, start_date, end_date)

        # 价格分布图
        price_distribution = self.generate_price_distribution(seller)

        # 品牌分布图
        brand_distribution = self.generate_brand_distribution(seller)

        return {
            'sales_trend': sales_trend,
            'price_distribution': price_distribution,
            'brand_distribution': brand_distribution
        }

    def generate_sales_trend(self, seller, start_date, end_date):
        """生成销售趋势数据"""
        # 按天分组统计销售额
        orders = Order.objects.filter(
            seller=seller,
            status='completed',
            completed_at__range=[start_date, end_date]
        ).extra({
            'day': "DATE(completed_at)"
        }).values('day').annotate(
            daily_sales=Sum('price'),
            daily_orders=Count('id')
        ).order_by('day')

        labels = []
        values = []

        for order in orders:
            labels.append(order['day'].strftime('%m-%d'))
            values.append(float(order['daily_sales'] or 0))

        return {
            'labels': labels,
            'values': values
        }

    def generate_price_distribution(self, seller):
        """生成价格分布数据"""
        vehicles = Vehicle.objects.filter(seller=seller, status__in=['listed', 'pending_review'])

        # 价格区间统计
        price_ranges = {
            '0-100k': 0,
            '100k-200k': 0,
            '200k-300k': 0,
            '300k-500k': 0,
            '500k+': 0
        }

        for vehicle in vehicles:
            price = float(vehicle.price)
            if price < 100000:
                price_ranges['0-100k'] += 1
            elif price < 200000:
                price_ranges['100k-200k'] += 1
            elif price < 300000:
                price_ranges['200k-300k'] += 1
            elif price < 500000:
                price_ranges['300k-500k'] += 1
            else:
                price_ranges['500k+'] += 1

        return {
            'labels': list(price_ranges.keys()),
            'values': list(price_ranges.values())
        }

    def generate_brand_distribution(self, seller):
        """生成品牌分布数据"""
        vehicles = Vehicle.objects.filter(seller=seller, status__in=['listed', 'pending_review'])

        brand_stats = vehicles.values('brand__name').annotate(
            count=Count('id')
        ).order_by('-count')[:6]  # 取前6个品牌

        labels = [stat['brand__name'] for stat in brand_stats]
        values = [stat['count'] for stat in brand_stats]

        return {
            'labels': labels,
            'values': values
        }
