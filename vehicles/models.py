"""
车辆管理模块模型
包含品牌、类型、车辆、定价、收藏等模型
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class CarBrand(models.Model):
    """
    汽车品牌模型
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='品牌名称')
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True, verbose_name='品牌logo')
    country = models.CharField(max_length=50, choices=[('china', '中国'), ('import', '进口')], default='import', verbose_name='国家/地区')
    description = models.TextField(null=True, blank=True, verbose_name='品牌描述')
    official_website = models.URLField(null=True, blank=True, verbose_name='官方网站')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'car_brands'
        verbose_name = '车品牌'
        verbose_name_plural = '车品牌'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class CarType(models.Model):
    """
    汽车类型/分类模型
    支持多级分类
    """
    name = models.CharField(max_length=100, verbose_name='类型名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name='父类别')
    description = models.TextField(null=True, blank=True, verbose_name='类型描述')
    icon = models.ImageField(upload_to='type_icons/', null=True, blank=True, verbose_name='图标')
    order_weight = models.IntegerField(default=0, verbose_name='排序权重')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'car_types'
        verbose_name = '车类型'
        verbose_name_plural = '车类型'
        ordering = ['order_weight', '-created_at']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name


class Vehicle(models.Model):
    """
    车辆信息模型
    """
    # 车辆状态选择
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending_review', '待审核'),
        ('listed', '在售'),
        ('sold', '已售'),
        ('delisted', '已下架'),
        ('maintenance', '维修中'),
        ('rejected', '审核拒绝'),
    )

    # 审核状态选择
    REVIEW_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )

    # 基本信息
    vin = models.CharField(max_length=30, unique=True, verbose_name='VIN码')
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='vehicles', verbose_name='品牌')
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles', verbose_name='车型类型')
    model_name = models.CharField(max_length=100, verbose_name='车型名称')
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2100)], verbose_name='年份')

    # 车况信息
    color = models.CharField(max_length=50, verbose_name='车身颜色')
    transmission = models.CharField(max_length=20, choices=[('manual', '手动'), ('auto', '自动'), ('cvt', 'CVT')], verbose_name='变速箱')
    emission_standard = models.CharField(max_length=50, choices=[('euro1', '欧I'), ('euro2', '欧II'), ('euro3', '欧III'), ('euro4', '欧IV'), ('euro5', '欧V'), ('euro6', '欧VI')], verbose_name='排放标准')
    fuel_type = models.CharField(max_length=50, choices=[('gasoline', '汽油'), ('diesel', '柴油'), ('electric', '电动'), ('hybrid', '混合动力')], verbose_name='燃油类型')
    mileage = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='行驶里程(km)')

    # 时间信息
    plate_date = models.DateField(verbose_name='上牌时间')
    first_owner_date = models.DateField(null=True, blank=True, verbose_name='首次过户时间')

    # 描述信息
    description = models.TextField(verbose_name='车况描述')
    highlights = models.JSONField(default=list, verbose_name='亮点标签')

    # 卖家信息
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', verbose_name='卖家')

    # 价格信息
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')

    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='车辆状态')
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending', verbose_name='审核状态')
    review_notes = models.TextField(null=True, blank=True, verbose_name='审核备注')

    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    favorite_count = models.IntegerField(default=0, verbose_name='收藏次数')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    listed_at = models.DateTimeField(null=True, blank=True, verbose_name='上架时间')
    sold_at = models.DateTimeField(null=True, blank=True, verbose_name='成交时间')

    class Meta:
        db_table = 'vehicles'
        verbose_name = '车辆'
        verbose_name_plural = '车辆'
        indexes = [
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-view_count']),
        ]

    def __str__(self):
        return f"{self.brand.name} {self.model_name} ({self.year})"


class VehiclePhoto(models.Model):
    """
    车辆照片模型
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='photos', verbose_name='车辆')
    image = models.ImageField(upload_to='vehicle_images/', verbose_name='图片')
    thumbnail = models.ImageField(upload_to='vehicle_thumbnails/', null=True, blank=True, verbose_name='缩略图')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_main = models.BooleanField(default=False, verbose_name='是否为主图')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        db_table = 'vehicle_photos'
        verbose_name = '车辆照片'
        verbose_name_plural = '车辆照片'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['vehicle', 'is_main']),
        ]

    def __str__(self):
        return f"{self.vehicle.model_name}的照片"


class VehiclePrice(models.Model):
    """
    车辆定价模型
    用于记录AI定价建议和价格变化
    """
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='price_info', verbose_name='车辆')
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='建议价格')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最低价格')
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最高价格')
    confidence_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], verbose_name='置信度')
    pricing_model = models.CharField(max_length=100, null=True, blank=True, verbose_name='定价模型版本')
    pricing_reason = models.TextField(null=True, blank=True, verbose_name='定价依据')

    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'vehicle_prices'
        verbose_name = '车辆定价'
        verbose_name_plural = '车辆定价'

    def __str__(self):
        return f"{self.vehicle.model_name}的定价"


class VehiclePriceHistory(models.Model):
    """
    车辆价格变化历史
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='price_history', verbose_name='车辆')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='旧价格')
    new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='新价格')
    change_reason = models.CharField(max_length=255, verbose_name='变化原因')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='变化时间')

    class Meta:
        db_table = 'vehicle_price_history'
        verbose_name = '价格变化历史'
        verbose_name_plural = '价格变化历史'
        ordering = ['-changed_at']


class Favorite(models.Model):
    """
    用户收藏模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='车辆')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'favorites'
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ('user', 'vehicle')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['vehicle']),
        ]

    def __str__(self):
        return f"{self.user.username}收藏了{self.vehicle.model_name}"


class Review(models.Model):
    """
    评价/点评模型
    """
    # 评价类型
    REVIEW_TYPE_CHOICES = (
        ('seller', '对卖家的评价'),
        ('buyer', '对买家的评价'),
        ('vehicle', '对车辆的评价'),
    )

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='vehicle_reviews', null=True, blank=True, verbose_name='订单')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_reviews', verbose_name='评价者')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews', null=True, blank=True, verbose_name='被评价者')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True, verbose_name='车辆')

    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='评分')
    content = models.TextField(verbose_name='评价内容')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES, default='seller', verbose_name='评价类型')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')

    seller_reply = models.TextField(null=True, blank=True, verbose_name='卖家回复')
    seller_reply_time = models.DateTimeField(null=True, blank=True, verbose_name='卖家回复时间')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews'
        verbose_name = '评价'
        verbose_name_plural = '评价'
        indexes = [
            models.Index(fields=['reviewed_user', '-created_at']),
            models.Index(fields=['vehicle', '-rating']),
        ]

    def __str__(self):
        return f"{self.reviewer.username}给{self.reviewed_user.username if self.reviewed_user else self.vehicle.model_name}的评价"