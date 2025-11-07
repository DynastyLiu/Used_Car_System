from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, Count
from .models import Order, OrderMessage, OrderReview, OrderPayment
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderMessageSerializer,
    OrderReviewSerializer, OrderPaymentSerializer
)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """根据不同的action使用不同的序列化器"""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """只能查看自己作为买家或卖家的订单"""
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user))

    def create(self, request, *args, **kwargs):
        """创建订单时处理钱包支付"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    'message': '购买成功！',
                    'order': serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError as e:
            # 处理验证错误（余额不足、密码错误等）
            error_message = str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """确认付款"""
        order = self.get_object()

        if order.buyer != request.user:
            return Response({'error': '只有买家可以确认付款'}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'pending_payment':
            return Response({'error': '订单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()

        return Response({'message': '付款确认成功'})

    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        """确认收货"""
        order = self.get_object()

        if order.buyer != request.user:
            return Response({'error': '只有买家可以确认收货'}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'paid':
            return Response({'error': '订单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()

        return Response({'message': '收货确认成功'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()

        if order.buyer != request.user:
            return Response({'error': '只有买家可以取消订单'}, status=status.HTTP_403_FORBIDDEN)

        if order.status in ['completed', 'cancelled']:
            return Response({'error': '订单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()

        return Response({'message': '订单取消成功'})


class OrderMessageViewSet(viewsets.ModelViewSet):
    serializer_class = OrderMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderMessage.objects.filter(order_id=self.kwargs['order_pk'])

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user,
            order_id=self.kwargs['order_pk']
        )


class OrderReviewViewSet(viewsets.ModelViewSet):
    serializer_class = OrderReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderReview.objects.filter(order_id=self.kwargs['order_pk'])

    def perform_create(self, serializer):
        serializer.save(
            reviewer=self.request.user,
            order_id=self.kwargs['order_pk']
        )


class OrderPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = OrderPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderPayment.objects.filter(order_id=self.kwargs['order_pk'])

    def perform_create(self, serializer):
        serializer.save(order_id=self.kwargs['order_pk'])