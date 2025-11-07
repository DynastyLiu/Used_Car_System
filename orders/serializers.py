from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from decimal import Decimal
from django.db import transaction
from .models import Order, OrderMessage, OrderReview, OrderPayment
from users.models import WalletTransaction

class OrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    can_confirm = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer', 'buyer_name', 'seller', 'seller_name',
            'vehicle', 'vehicle_info', 'price', 'deposit', 'status', 'status_display',
            'buyer_note', 'seller_note', 'created_at', 'paid_at', 'completed_at',
            'can_cancel', 'can_confirm', 'can_review'
        ]
        read_only_fields = ['order_number', 'buyer', 'seller', 'created_at']

    def get_vehicle_info(self, obj):
        vehicle = obj.vehicle
        main_photo = vehicle.photos.filter(is_main=True).first()
        return {
            'id': vehicle.id,
            'brand_name': vehicle.brand.name,
            'model_name': vehicle.model_name,
            'year': vehicle.year,
            'mileage': vehicle.mileage,
            'main_photo': main_photo.image.url if main_photo else None
        }

    def get_can_cancel(self, obj):
        """判断是否可以取消订单"""
        return obj.status in ['pending_payment']

    def get_can_confirm(self, obj):
        """判断是否可以确认操作"""
        return obj.status in ['pending_payment', 'paid']

    def get_can_review(self, obj):
        """判断是否可以评价"""
        return obj.status == 'completed'


class OrderCreateSerializer(serializers.ModelSerializer):
    payment_password = serializers.CharField(write_only=True, required=True)
    buyer_phone = serializers.CharField(required=False, allow_blank=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    delivery_time = serializers.DateTimeField(required=False, allow_null=True)
    vehicle_color = serializers.CharField(required=False, allow_blank=True)
    vehicle_model_type = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            'vehicle', 'price', 'buyer_note', 'payment_password',
            'buyer_phone', 'delivery_address', 'delivery_time',
            'vehicle_color', 'vehicle_model_type'
        ]

    def create(self, validated_data):
        payment_password = validated_data.pop('payment_password')
        buyer = self.context['request'].user
        vehicle = validated_data['vehicle']
        price = Decimal(str(validated_data['price']))

        # 1. 验证支付密码
        if not buyer.payment_password:
            raise serializers.ValidationError('您还未设置交易密码，请先设置密码')

        if not check_password(payment_password, buyer.payment_password):
            raise serializers.ValidationError('交易密码不正确，请重新输入')

        # 2. 检查钱包余额
        buyer_profile = buyer.profile
        if buyer_profile.balance < price:
            raise serializers.ValidationError(f'您的余额不足，无法购买。余额: ¥{buyer_profile.balance}，需要: ¥{price}')

        # 3. 使用数据库事务确保原子性
        try:
            with transaction.atomic():
                # 生成订单号
                order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}"

                # 扣款
                buyer_profile.balance -= price
                buyer_profile.save()

                # 创建订单
                order = Order.objects.create(
                    order_number=order_number,
                    buyer=buyer,
                    seller=vehicle.seller,
                    vehicle=vehicle,
                    price=price,
                    status='paid',
                    paid_at=timezone.now(),
                    buyer_note=validated_data.get('buyer_note', ''),
                    buyer_phone=validated_data.get('buyer_phone', ''),
                    delivery_address=validated_data.get('delivery_address', ''),
                    delivery_time=validated_data.get('delivery_time'),
                    vehicle_color=validated_data.get('vehicle_color', ''),
                    vehicle_model_type=validated_data.get('vehicle_model_type', '')
                )

                # 创建钱包交易记录
                WalletTransaction.objects.create(
                    user=buyer,
                    amount=price,
                    transaction_type='purchase',
                    payment_method='wallet',
                    status='success',
                    description=f'购买车辆: {vehicle.brand.name} {vehicle.model_name}',
                    order_number=order_number
                )

                return order

        except Exception as e:
            raise serializers.ValidationError(f'购买失败: {str(e)}')


class OrderMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = OrderMessage
        fields = ['id', 'sender', 'sender_name', 'content', 'message_type', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']


class OrderReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = OrderReview
        fields = ['id', 'rating', 'content', 'reviewer', 'reviewer_name', 'is_anonymous', 'created_at']
        read_only_fields = ['reviewer', 'created_at']


class OrderPaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderPayment
        fields = [
            'id', 'payment_method', 'payment_method_display', 'transaction_id',
            'amount', 'status', 'status_display', 'created_at', 'paid_at'
        ]
        read_only_fields = ['transaction_id', 'status', 'paid_at']