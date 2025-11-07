#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卖家中心序列化器
"""
from rest_framework import serializers
from users.models import User
from orders.models import Order, OrderReview
from vehicles.models import Vehicle, VehiclePrice, VehiclePriceHistory, CarBrand


class SellerOrderSerializer(serializers.ModelSerializer):
    """卖家订单序列化器"""
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    vehicle_title = serializers.SerializerMethodField()
    vehicle_model = serializers.CharField(source='vehicle.model_name', read_only=True)
    brand_name = serializers.CharField(source='vehicle.brand.name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer_name', 'vehicle_title', 'vehicle_model',
            'brand_name', 'vehicle_name', 'price', 'deposit', 'status', 'status_display',
            'buyer_note', 'seller_note', 'created_at', 'paid_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'buyer_name', 'vehicle_title', 'vehicle_model',
            'brand_name', 'vehicle_name', 'created_at', 'paid_at', 'completed_at'
        ]

    def _compose_vehicle_name(self, vehicle):
        if not vehicle:
            return ''
        parts = []
        if getattr(vehicle, 'brand', None):
            parts.append(vehicle.brand.name)
        if getattr(vehicle, 'model_name', None):
            parts.append(vehicle.model_name)
        name = ' '.join(part for part in parts if part).strip()
        return name or (vehicle.model_name or '')

    def get_vehicle_title(self, obj):
        return self._compose_vehicle_name(getattr(obj, 'vehicle', None))

    def get_vehicle_name(self, obj):
        return self.get_vehicle_title(obj)


class VehiclePriceSerializer(serializers.ModelSerializer):
    """车辆价格序列化器"""
    vehicle_title = serializers.SerializerMethodField()
    vehicle_model = serializers.CharField(source='vehicle.model_name', read_only=True)
    brand_name = serializers.CharField(source='vehicle.brand.name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(source='vehicle.price', max_digits=10, decimal_places=2, read_only=True)
    ai_suggested_price = serializers.SerializerMethodField()
    market_avg_price = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()

    class Meta:
        model = VehiclePrice
        fields = [
            'id', 'vehicle', 'vehicle_title', 'vehicle_model', 'brand_name', 'vehicle_name',
            'current_price', 'suggested_price', 'min_price', 'max_price',
            'confidence_score', 'pricing_reason', 'updated_at', 'trend',
            'ai_suggested_price', 'market_avg_price'
        ]
        read_only_fields = ['id', 'updated_at', 'trend', 'vehicle_name', 'vehicle_title', 'ai_suggested_price', 'market_avg_price']

    def _compose_vehicle_name(self, vehicle):
        if not vehicle:
            return ''
        parts = []
        if getattr(vehicle, 'brand', None):
            parts.append(vehicle.brand.name)
        if getattr(vehicle, 'model_name', None):
            parts.append(vehicle.model_name)
        name = ' '.join(part for part in parts if part).strip()
        return name or (vehicle.model_name or '')

    def get_vehicle_title(self, obj):
        return self._compose_vehicle_name(getattr(obj, 'vehicle', None))

    def get_vehicle_name(self, obj):
        return self.get_vehicle_title(obj)

    def get_ai_suggested_price(self, obj):
        return obj.suggested_price

    def get_market_avg_price(self, obj):
        base = obj.max_price or obj.suggested_price or getattr(obj.vehicle, 'price', None)
        return float(base) if base is not None else None

    def get_trend(self, obj):
        """计算价格趋势"""
        if obj.suggested_price and obj.vehicle.price:
            try:
                suggested = float(obj.suggested_price)
                current = float(obj.vehicle.price)
            except (TypeError, ValueError):
                return 'stable'
            if suggested > current:
                return 'up'
            if suggested < current:
                return 'down'
        return 'stable'


class VehiclePriceHistorySerializer(serializers.ModelSerializer):
    """价格历史序列化器"""
    # 注意：VehiclePriceHistory模型可能没有changed_by字段
    # changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = VehiclePriceHistory
        fields = [
            'id', 'old_price', 'new_price', 'change_reason',
            'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']


class SellerReviewSerializer(serializers.ModelSerializer):
    """卖家评价序列化器"""
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    vehicle_title = serializers.SerializerMethodField()
    vehicle_model = serializers.CharField(source='order.vehicle.model_name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()
    replied = serializers.SerializerMethodField()
    reply_content = serializers.SerializerMethodField()

    class Meta:
        model = OrderReview
        fields = [
            'id', 'order', 'reviewer_name', 'vehicle_title', 'vehicle_model', 'vehicle_name',
            'rating', 'content', 'is_anonymous', 'replied', 'reply_content',
            'created_at'
        ]
        read_only_fields = [
            'id', 'reviewer_name', 'vehicle_title', 'vehicle_model', 'vehicle_name',
            'created_at', 'replied', 'reply_content'
        ]

    def _compose_vehicle_name(self, review):
        vehicle = getattr(review.order, 'vehicle', None)
        if not vehicle:
            return ''
        parts = []
        if getattr(vehicle, 'brand', None):
            parts.append(vehicle.brand.name)
        if getattr(vehicle, 'model_name', None):
            parts.append(vehicle.model_name)
        name = ' '.join(part for part in parts if part).strip()
        return name or (vehicle.model_name or '')

    def get_vehicle_title(self, obj):
        return self._compose_vehicle_name(obj)

    def get_vehicle_name(self, obj):
        return self.get_vehicle_title(obj)

    def get_replied(self, obj):
        """检查是否已回复"""
        return bool(obj.order.seller_note)

    def get_reply_content(self, obj):
        """获取回复内容"""
        return obj.order.seller_note


class SellerAnalyticsSerializer(serializers.Serializer):
    """卖家统计数据序列化器"""
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    avg_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.FloatField()
    revenue_trend = serializers.FloatField()
    orders_trend = serializers.FloatField()
    price_trend = serializers.FloatField()
    conversion_trend = serializers.FloatField()


class SellerOverviewSerializer(serializers.Serializer):
    """卖家概览数据序列化器"""
    total_vehicles = serializers.IntegerField()
    listed_vehicles = serializers.IntegerField()
    sold_vehicles = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    recent_views = serializers.IntegerField()


class ChartDataSerializer(serializers.Serializer):
    """图表数据序列化器"""
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.FloatField())
