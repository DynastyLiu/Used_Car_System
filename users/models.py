"""
用户模块模型定义
包含用户、身份认证、地址等相关模型
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class User(AbstractUser):
    """
    扩展的用户模型
    """
    # 用户类型选择
    USER_TYPE_CHOICES = (
        ('buyer', '买家'),
        ('seller', '卖家'),
        ('admin', '管理员'),
    )

    # 账户状态选择
    ACCOUNT_STATUS_CHOICES = (
        ('normal', '正常'),
        ('disabled', '禁用'),
        ('frozen', '冻结'),
    )

    # 认证状态选择
    AUTH_STATUS_CHOICES = (
        ('unverified', '未认证'),
        ('pending', '待审核'),
        ('verified', '已认证'),
        ('rejected', '认证拒绝'),
    )

    # 基本字段
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='手机号')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='buyer', verbose_name='用户类型')
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='normal', verbose_name='账户状态')

    # 头像和个人信息
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='昵称')
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女'), ('other', '其他')],
                            null=True, blank=True, verbose_name='性别')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name='个人简介')
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name='所在地区')

    # 认证信息
    real_name_auth_status = models.CharField(max_length=20, choices=AUTH_STATUS_CHOICES, default='unverified', verbose_name='实名认证状态')
    id_number = models.CharField(max_length=18, unique=True, null=True, blank=True, verbose_name='身份证号')
    id_front_image = models.ImageField(upload_to='id_images/', null=True, blank=True, verbose_name='身份证正面')
    id_back_image = models.ImageField(upload_to='id_images/', null=True, blank=True, verbose_name='身份证反面')

    # 银行卡信息（卖家）
    bank_account_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='开户人名称')
    bank_card_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='银行卡号')
    bank_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='开户行')

    # 账户统计
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='最后登录IP')
    login_count = models.IntegerField(default=0, verbose_name='登录次数')
    failed_login_count = models.IntegerField(default=0, verbose_name='失败登录次数')
    last_failed_login = models.DateTimeField(null=True, blank=True, verbose_name='最后失败登录时间')

    # 钱包信息
    payment_password = models.CharField(max_length=128, null=True, blank=True, verbose_name='交易密码')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['account_status']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class UserProfile(models.Model):
    """
    用户档案 - 存储额外的用户信息
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    total_purchases = models.IntegerField(default=0, verbose_name='总购买数')
    total_sales = models.IntegerField(default=0, verbose_name='总销售数')
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], verbose_name='平均评分')
    total_reviews = models.IntegerField(default=0, verbose_name='评价总数')

    # 卖家信息
    shop_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='店铺名称')
    shop_logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True, verbose_name='店铺logo')
    shop_description = models.TextField(null=True, blank=True, verbose_name='店铺描述')
    shop_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='店铺电话')
    shop_address = models.CharField(max_length=255, null=True, blank=True, verbose_name='店铺地址')

    # 账户余额
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name='账户余额')
    frozen_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name='冻结余额')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'

    def __str__(self):
        return f"{self.user.username}的档案"


class UserAddress(models.Model):
    """
    用户地址 - 收货地址管理
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    name = models.CharField(max_length=100, verbose_name='收货人')
    phone = models.CharField(max_length=20, verbose_name='电话')
    province = models.CharField(max_length=50, verbose_name='省')
    city = models.CharField(max_length=50, verbose_name='市')
    district = models.CharField(max_length=50, verbose_name='区')
    address = models.CharField(max_length=255, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='邮编')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_addresses'
        verbose_name = '用户地址'
        verbose_name_plural = '用户地址'

    def __str__(self):
        return f"{self.name} - {self.province}{self.city}{self.district}"


class UserLoginHistory(models.Model):
    """
    用户登录历史记录
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history', verbose_name='用户')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.CharField(max_length=500, verbose_name='用户代理')
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='登录时间')
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name='登出时间')
    success = models.BooleanField(default=True, verbose_name='是否成功')

    class Meta:
        db_table = 'user_login_history'
        verbose_name = '登录历史'
        verbose_name_plural = '登录历史'
        indexes = [
            models.Index(fields=['user', '-login_time']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class UserOperationLog(models.Model):
    """
    用户操作日志
    """
    OPERATION_CHOICES = (
        ('login', '登录'),
        ('logout', '登出'),
        ('register', '注册'),
        ('password_change', '修改密码'),
        ('info_update', '更新信息'),
        ('vehicle_upload', '上传车辆'),
        ('vehicle_delete', '删除车辆'),
        ('place_order', '下订单'),
        ('cancel_order', '取消订单'),
        ('other', '其他'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operation_logs', verbose_name='用户')
    operation_type = models.CharField(max_length=50, choices=OPERATION_CHOICES, verbose_name='操作类型')
    description = models.TextField(verbose_name='操作描述')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.CharField(max_length=500, verbose_name='用户代理')
    status = models.CharField(max_length=20, choices=[('success', '成功'), ('failure', '失败')], default='success', verbose_name='状态')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'user_operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_operation_type_display()}"


class UserSearchHistory(models.Model):
    """
    用户搜索历史
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history', verbose_name='用户')
    keyword = models.CharField(max_length=255, verbose_name='搜索关键词')
    search_params = models.JSONField(default=dict, verbose_name='搜索参数')
    search_time = models.DateTimeField(auto_now_add=True, verbose_name='搜索时间')
    result_count = models.IntegerField(default=0, verbose_name='结果数量')

    class Meta:
        db_table = 'user_search_history'
        verbose_name = '搜索历史'
        verbose_name_plural = '搜索历史'
        indexes = [
            models.Index(fields=['user', '-search_time']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.keyword}"


class UserBrowsingHistory(models.Model):
    """
    用户浏览历史
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='browsing_history', verbose_name='用户')
    vehicle_id = models.IntegerField(verbose_name='车辆ID')
    browse_time = models.DateTimeField(auto_now_add=True, verbose_name='浏览时间')
    duration = models.IntegerField(default=0, verbose_name='浏览时长（秒）')

    class Meta:
        db_table = 'user_browsing_history'
        verbose_name = '浏览历史'
        verbose_name_plural = '浏览历史'
        indexes = [
            models.Index(fields=['user', '-browse_time']),
        ]

    def __str__(self):
        return f"{self.user.username} - 车辆{self.vehicle_id}"


class WalletTransaction(models.Model):
    """
    钱包交易记录
    """
    TRANSACTION_TYPE_CHOICES = (
        ('recharge', '充值'),
        ('purchase', '购买'),
        ('refund', '退款'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('wechat', '微信'),
        ('alipay', '支付宝'),
        ('bank', '银行卡'),
    )

    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('success', '成功'),
        ('failed', '失败'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions', verbose_name='用户')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name='交易类型')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True, verbose_name='支付方式')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    description = models.CharField(max_length=255, verbose_name='描述')
    order_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='关联订单号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wallet_transactions'
        verbose_name = '钱包交易记录'
        verbose_name_plural = '钱包交易记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - ¥{self.amount}"