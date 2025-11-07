"""
管理员控制台模型
"""
from django.db import models
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle

User = get_user_model()


class VehicleReview(models.Model):
    """
    车辆审核记录
    """
    REVIEW_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '审核拒绝'),
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='admin_reviews', verbose_name='车辆')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='vehicle_reviews', verbose_name='审核员')
    status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending', verbose_name='审核状态')
    review_note = models.TextField(null=True, blank=True, verbose_name='审核备注')
    review_time = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'vehicle_reviews'
        verbose_name = '车辆审核'
        verbose_name_plural = '车辆审核'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reviewer', '-review_time']),
        ]

    def __str__(self):
        return f"车辆审核 - {self.vehicle.brand.name} {self.vehicle.model_name} ({self.get_status_display()})"


class UserAuthenticationReview(models.Model):
    """
    用户实名认证审核记录
    """
    REVIEW_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '审核拒绝'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_reviews', verbose_name='用户')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='auth_reviews_made', verbose_name='审核员')
    status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending', verbose_name='审核状态')
    review_note = models.TextField(null=True, blank=True, verbose_name='审核备注')
    review_time = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')

    # 审核时的快照数据，防止用户修改后影响审核结果
    id_number_snapshot = models.CharField(max_length=18, null=True, blank=True, verbose_name='身份证号快照')
    id_front_image_snapshot = models.ImageField(upload_to='review_id_images/', null=True, blank=True, verbose_name='身份证正面快照')
    id_back_image_snapshot = models.ImageField(upload_to='review_id_images/', null=True, blank=True, verbose_name='身份证反面快照')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_auth_reviews'
        verbose_name = '用户认证审核'
        verbose_name_plural = '用户认证审核'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reviewer', '-review_time']),
        ]

    def __str__(self):
        return f"用户认证审核 - {self.user.username} ({self.get_status_display()})"


class SystemReport(models.Model):
    """
    系统举报记录
    """
    REPORT_TYPE_CHOICES = (
        ('vehicle', '车辆信息举报'),
        ('user', '用户行为举报'),
        ('fraud', '欺诈行为举报'),
        ('other', '其他举报'),
    )

    REPORT_STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已处理'),
        ('dismissed', '已忽略'),
    )

    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_made', verbose_name='举报人')
    reported_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_received', verbose_name='被举报用户')
    reported_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='reports', verbose_name='被举报车辆')

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='举报类型')
    title = models.CharField(max_length=200, verbose_name='举报标题')
    description = models.TextField(verbose_name='举报描述')
    evidence_images = models.JSONField(default=list, verbose_name='证据图片')

    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending', verbose_name='处理状态')
    handler = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='handled_reports', verbose_name='处理人')
    handling_note = models.TextField(null=True, blank=True, verbose_name='处理备注')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')

    class Meta:
        db_table = 'system_reports'
        verbose_name = '系统举报'
        verbose_name_plural = '系统举报'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['report_type', '-created_at']),
            models.Index(fields=['handler', '-updated_at']),
        ]

    def __str__(self):
        return f"举报 - {self.title} ({self.get_status_display()})"


class AdminOperationLog(models.Model):
    """
    管理员操作日志
    """
    OPERATION_CHOICES = (
        ('vehicle_approve', '审核通过车辆'),
        ('vehicle_reject', '审核拒绝车辆'),
        ('user_auth_approve', '审核通过用户认证'),
        ('user_auth_reject', '审核拒绝用户认证'),
        ('report_handle', '处理举报'),
        ('user_ban', '封禁用户'),
        ('user_unban', '解封用户'),
        ('vehicle_remove', '下架车辆'),
        ('system_config', '系统配置修改'),
        ('other', '其他操作'),
    )

    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_operations', verbose_name='管理员')
    operation_type = models.CharField(max_length=50, choices=OPERATION_CHOICES, verbose_name='操作类型')
    target_type = models.CharField(max_length=20, verbose_name='目标类型')  # user, vehicle, report等
    target_id = models.IntegerField(verbose_name='目标ID')
    description = models.TextField(verbose_name='操作描述')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.CharField(max_length=500, null=True, blank=True, verbose_name='用户代理')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'admin_operation_logs'
        verbose_name = '管理员操作日志'
        verbose_name_plural = '管理员操作日志'
        indexes = [
            models.Index(fields=['admin', '-created_at']),
            models.Index(fields=['operation_type', '-created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        return f"{self.admin.username} - {self.get_operation_type_display()} - {self.created_at}"