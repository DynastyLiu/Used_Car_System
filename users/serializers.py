"""
用户模块序列化器
用于API的数据序列化和验证
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from django.db import models
from .models import User, UserProfile, UserAddress, UserLoginHistory, UserBrowsingHistory, WalletTransaction


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='确认密码'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password', 'password2', 'user_type')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, data):
        """确认两个密码是否一致"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                _("密码不一致。")
            )
        return data

    def validate_password(self, value):
        """确认密码强度"""
        if len(value) < 8:
            raise serializers.ValidationError(
                _("密码至少需要8个字符。")
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                _("密码必须包含至少一个大写字母。")
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                _("密码必须包含至少一个数字。")
            )
        return value

    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password2')

        # 处理电话号码：如果为空字符串则设置为None
        phone = validated_data.get('phone')
        if phone == '' or phone is None:
            phone = None

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=phone,
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'buyer')
        )
        # 创建用户档案（使用get_or_create避免重复创建）
        UserProfile.objects.get_or_create(user=user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义Token序列化器 - 登录时返回用户信息
    支持username/email/phone三种方式登录
    """
    def validate(self, attrs):
        # 获取输入的用户标识符和密码
        identifier = attrs.get('username')  # 可以是username、email或phone
        password = attrs.get('password')

        # 尝试用username、email或phone查找用户
        user = User.objects.filter(
            models.Q(username=identifier) |
            models.Q(email=identifier) |
            models.Q(phone=identifier)
        ).first()

        # 验证用户和密码
        if not user or not user.check_password(password):
            # 用户不存在或密码错误，抛出验证错误
            raise serializers.ValidationError(
                {'non_field_errors': ['用户名/邮箱/手机号或密码错误']}
            )

        # 检查用户是否被激活
        if not user.is_active:
            raise serializers.ValidationError(
                {'non_field_errors': ['该账户已被禁用，请联系管理员']}
            )

        # 将attrs['username']设置为实际的username，以便parent.validate()使用
        attrs['username'] = user.username
        attrs['password'] = password

        # 调用parent的validate方法生成token
        try:
            data = super().validate(attrs)
        except serializers.ValidationError as e:
            # 如果parent仍然抛出错误，使用我们自己的错误信息
            raise serializers.ValidationError(
                {'non_field_errors': ['用户名/邮箱/手机号或密码错误']}
            )

        # 添加用户信息到响应
        data.update({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'user_type': user.user_type,
                'is_verified': user.real_name_auth_status == 'verified',
            }
        })

        # 保存user对象以供view使用
        self.user = user

        return data


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'user_type', 'account_status',
                  'real_name_auth_status', 'nickname', 'avatar', 'gender', 'birth_date',
                  'bio', 'location', 'date_joined', 'profile')
        read_only_fields = ('id', 'date_joined', 'real_name_auth_status')

    def get_profile(self, obj):
        """获取用户档案信息"""
        try:
            profile = obj.profile
            return {
                'total_purchases': profile.total_purchases,
                'total_sales': profile.total_sales,
                'average_rating': profile.average_rating,
                'total_reviews': profile.total_reviews,
                'shop_name': profile.shop_name,
                'shop_description': profile.shop_description,
                'balance': float(profile.balance),
            }
        except UserProfile.DoesNotExist:
            return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户信息更新序列化器
    """
    class Meta:
        model = User
        fields = ('nickname', 'gender', 'birth_date', 'bio', 'location', 'avatar')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户档案序列化器
    """
    class Meta:
        model = UserProfile
        fields = ('shop_name', 'shop_description', 'shop_phone', 'shop_address')


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    class Meta:
        model = UserAddress
        fields = ('id', 'name', 'phone', 'province', 'city', 'district',
                  'address', 'postal_code', 'is_default')

    def create(self, validated_data):
        """创建地址，如果设置为默认则先取消其他默认地址"""
        if validated_data.get('is_default', False):
            UserAddress.objects.filter(
                user=self.context['request'].user,
                is_default=True
            ).update(is_default=False)

        return super().create(validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("新密码不一致")

        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError("旧密码错误")

        return data


class PasswordResetSerializer(serializers.Serializer):
    """
    密码重置序列化器
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """验证邮箱是否存在"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱未注册")
        return value


class UserRealNameAuthSerializer(serializers.ModelSerializer):
    """
    用户实名认证序列化器
    """
    class Meta:
        model = User
        fields = ('id_number', 'id_front_image', 'id_back_image')
        extra_kwargs = {
            'id_number': {'required': True},
            'id_front_image': {'required': True},
            'id_back_image': {'required': True},
        }

    def validate(self, data):
        """验证实名认证信息"""
        id_number = data.get('id_number')

        # 检查身份证号格式
        if len(id_number) != 18:
            raise serializers.ValidationError("身份证号格式不正确")

        # 检查是否已经被使用
        if User.objects.filter(id_number=id_number).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("该身份证号已被使用")

        # 更新认证状态为待审核
        if self.instance:
            self.instance.real_name_auth_status = 'pending'
            self.instance.save(update_fields=['real_name_auth_status'])

        return data


class UserSellerAuthSerializer(serializers.ModelSerializer):
    """
    用户卖家认证序列化器
    """
    class Meta:
        model = User
        fields = ('bank_account_name', 'bank_card_number', 'bank_name')
        extra_kwargs = {
            'bank_account_name': {'required': True},
            'bank_card_number': {'required': True},
            'bank_name': {'required': True},
        }


class UserLoginHistorySerializer(serializers.ModelSerializer):
    """
    用户登录历史序列化器
    """
    class Meta:
        model = UserLoginHistory
        fields = ('ip_address', 'user_agent', 'login_time', 'logout_time', 'success')
        read_only_fields = ('login_time', 'logout_time', 'success')


class UserBrowsingHistorySerializer(serializers.ModelSerializer):
    """
    用户浏览历史序列化器
    """
    # 用于读取时获取车辆详细信息
    brand_name = serializers.SerializerMethodField(read_only=True)
    model_name = serializers.SerializerMethodField(read_only=True)
    year = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    color = serializers.SerializerMethodField(read_only=True)
    mileage = serializers.SerializerMethodField(read_only=True)
    main_photo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserBrowsingHistory
        fields = ('id', 'vehicle_id', 'brand_name', 'model_name', 'year', 'price', 'color', 'mileage', 'main_photo', 'browse_time', 'duration')
        read_only_fields = ('browse_time', 'id')

    def _get_vehicle_cache(self, obj):
        """获取车辆对象（带缓存）"""
        # 使用实例属性缓存，避免重复查询
        cache_key = f'_vehicle_{obj.vehicle_id}'
        if not hasattr(self, cache_key):
            from vehicles.models import Vehicle
            try:
                vehicle = Vehicle.objects.select_related('brand').prefetch_related('photos').get(id=obj.vehicle_id)
                setattr(self, cache_key, vehicle)
            except Vehicle.DoesNotExist:
                setattr(self, cache_key, None)
        return getattr(self, cache_key)

    def get_brand_name(self, obj):
        """获取品牌名称"""
        vehicle = self._get_vehicle_cache(obj)
        return vehicle.brand.name if vehicle and vehicle.brand else '未知品牌'

    def get_model_name(self, obj):
        """获取车型名称"""
        vehicle = self._get_vehicle_cache(obj)
        return vehicle.model_name if vehicle else '未知型号'

    def get_year(self, obj):
        """获取年份"""
        vehicle = self._get_vehicle_cache(obj)
        return vehicle.year if vehicle else None

    def get_price(self, obj):
        """获取价格"""
        vehicle = self._get_vehicle_cache(obj)
        return vehicle.price if vehicle else 0

    def get_color(self, obj):
        """获取颜色"""
        vehicle = self._get_vehicle_cache(obj)
        return vehicle.color if vehicle else '未知'

    def get_mileage(self, obj):
        """获取里程"""
        vehicle = self._get_vehicle_cache(obj)
        return vehicle.mileage if vehicle else 0

    def get_main_photo(self, obj):
        """获取车辆主图片"""
        vehicle = self._get_vehicle_cache(obj)
        if vehicle:
            photos = vehicle.photos.all()
            if photos:
                main_photo = next((p for p in photos if p.is_main), photos[0] if photos else None)
                if main_photo:
                    return main_photo.image.url
        return None

    def validate_vehicle_id(self, value):
        """验证车辆ID是否存在"""
        from vehicles.models import Vehicle
        if not Vehicle.objects.filter(id=value).exists():
            raise serializers.ValidationError('车辆不存在')
        return value


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    钱包交易记录序列化器
    """
    class Meta:
        model = WalletTransaction
        fields = ('id', 'amount', 'transaction_type', 'payment_method', 'status', 'description', 'order_number', 'created_at')
        read_only_fields = ('id', 'created_at')


class WalletInfoSerializer(serializers.Serializer):
    """
    钱包信息序列化器
    """
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    frozen_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    has_payment_password = serializers.SerializerMethodField()

    def get_has_payment_password(self, obj):
        """检查是否已设置交易密码"""
        return obj.payment_password is not None and obj.payment_password != ''