"""
管理员审核模块序列化器
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import VehicleReview, UserAuthenticationReview, SystemReport, AdminOperationLog
from vehicles.serializers import VehicleSerializer

User = get_user_model()


class VehicleReviewSerializer(serializers.ModelSerializer):
    """
    车辆审核序列化器
    """
    vehicle_info = serializers.SerializerMethodField()
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = VehicleReview
        fields = (
            'id', 'vehicle', 'vehicle_info', 'reviewer', 'reviewer_name',
            'status', 'review_note', 'review_time', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'reviewer', 'review_time', 'created_at', 'updated_at')

    def get_vehicle_info(self, obj):
        """获取车辆基本信息"""
        vehicle = obj.vehicle
        main_photo = vehicle.photos.filter(is_main=True).first()
        return {
            'id': vehicle.id,
            'brand_name': vehicle.brand.name,
            'model_name': vehicle.model_name,
            'year': vehicle.year,
            'price': vehicle.price,
            'mileage': vehicle.mileage,
            'main_photo': main_photo.image.url if main_photo else None,
            'seller_name': vehicle.seller.username,
            'created_at': vehicle.created_at,
        }

    def validate(self, data):
        """验证审核操作"""
        review = self.instance
        if review and review.status != 'pending':
            raise serializers.ValidationError("该审核已处理，无法重复操作")
        return data


class VehicleReviewActionSerializer(serializers.Serializer):
    """
    车辆审核操作序列化器
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    review_note = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    def validate_review_note(self, value):
        """拒绝时必须填写备注"""
        if self.initial_data.get('action') == 'reject' and not value:
            raise serializers.ValidationError("拒绝审核时必须填写拒绝原因")
        return value


class UserAuthenticationReviewSerializer(serializers.ModelSerializer):
    """
    用户实名认证审核序列化器
    """
    user_info = serializers.SerializerMethodField()
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = UserAuthenticationReview
        fields = (
            'id', 'user', 'user_info', 'reviewer', 'reviewer_name',
            'status', 'review_note', 'review_time',
            'id_number_snapshot', 'id_front_image_snapshot', 'id_back_image_snapshot',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'reviewer', 'review_time', 'created_at', 'updated_at')

    def get_user_info(self, obj):
        """获取用户基本信息"""
        user = obj.user
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'user_type': user.user_type,
            'created_at': user.created_at,
        }

    def validate(self, data):
        """验证审核操作"""
        review = self.instance
        if review and review.status != 'pending':
            raise serializers.ValidationError("该认证已审核，无法重复操作")
        return data


class UserAuthenticationReviewActionSerializer(serializers.Serializer):
    """
    用户认证审核操作序列化器
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    review_note = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    def validate_review_note(self, value):
        """拒绝时必须填写备注"""
        if self.initial_data.get('action') == 'reject' and not value:
            raise serializers.ValidationError("拒绝认证时必须填写拒绝原因")
        return value


class SystemReportSerializer(serializers.ModelSerializer):
    """
    系统举报序列化器
    """
    reporter_info = serializers.SerializerMethodField()
    reported_user_info = serializers.SerializerMethodField()
    reported_vehicle_info = serializers.SerializerMethodField()
    handler_info = serializers.SerializerMethodField()

    class Meta:
        model = SystemReport
        fields = (
            'id', 'reporter', 'reporter_info', 'reported_user', 'reported_user_info',
            'reported_vehicle', 'reported_vehicle_info', 'report_type', 'title', 'description',
            'evidence_images', 'status', 'handler', 'handler_info', 'handling_note',
            'created_at', 'updated_at', 'resolved_at'
        )
        read_only_fields = ('id', 'reporter', 'handler', 'resolved_at', 'created_at', 'updated_at')

    def get_reporter_info(self, obj):
        """获取举报人信息"""
        if obj.reporter:
            return {
                'id': obj.reporter.id,
                'username': obj.reporter.username,
            }
        return None

    def get_reported_user_info(self, obj):
        """获取被举报用户信息"""
        if obj.reported_user:
            return {
                'id': obj.reported_user.id,
                'username': obj.reported_user.username,
                'user_type': obj.reported_user.user_type,
            }
        return None

    def get_reported_vehicle_info(self, obj):
        """获取被举报车辆信息"""
        if obj.reported_vehicle:
            vehicle = obj.reported_vehicle
            return {
                'id': vehicle.id,
                'brand_name': vehicle.brand.name,
                'model_name': vehicle.model_name,
                'year': vehicle.year,
                'price': vehicle.price,
            }
        return None

    def get_handler_info(self, obj):
        """获取处理人信息"""
        if obj.handler:
            return {
                'id': obj.handler.id,
                'username': obj.handler.username,
            }
        return None


class SystemReportActionSerializer(serializers.Serializer):
    """
    举报处理操作序列化器
    """
    action = serializers.ChoiceField(
        choices=['processing', 'resolved', 'dismissed'],
        required=True
    )
    handling_note = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    def validate_handling_note(self, value):
        """某些操作需要填写备注"""
        action = self.initial_data.get('action')
        if action in ['resolved', 'dismissed'] and not value:
            action_text = {
                'resolved': '解决举报',
                'dismissed': '忽略举报'
            }
            raise serializers.ValidationError(f"{action_text[action]}时必须填写处理备注")
        return value


class AdminOperationLogSerializer(serializers.ModelSerializer):
    """
    管理员操作日志序列化器
    """
    admin_name = serializers.CharField(source='admin.username', read_only=True)

    class Meta:
        model = AdminOperationLog
        fields = (
            'id', 'admin', 'admin_name', 'operation_type', 'target_type',
            'target_id', 'description', 'ip_address', 'user_agent', 'created_at'
        )
        read_only_fields = ('id', 'admin', 'created_at')


class AdminDashboardSerializer(serializers.Serializer):
    """
    管理员仪表板数据序列化器
    """
    # 统计数据
    pending_vehicle_reviews = serializers.IntegerField()
    pending_user_auth_reviews = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_vehicles = serializers.IntegerField()
    today_new_users = serializers.IntegerField()
    today_new_vehicles = serializers.IntegerField()

    # 最近活动
    recent_reviews = VehicleReviewSerializer(many=True)
    recent_auth_reviews = UserAuthenticationReviewSerializer(many=True)
    recent_reports = SystemReportSerializer(many=True)
    recent_operations = AdminOperationLogSerializer(many=True)