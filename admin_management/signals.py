"""
管理员审核模块信号处理
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from vehicles.models import Vehicle
from users.models import User
from .models import VehicleReview, UserAuthenticationReview


@receiver(post_save, sender=Vehicle)
def create_vehicle_review(sender, instance, created, **kwargs):
    """
    车辆创建时自动创建审核记录
    """
    if created:
        VehicleReview.objects.create(
            vehicle=instance,
            status='pending'
        )


@receiver(post_save, sender=User)
def create_user_auth_review(sender, instance, created, **kwargs):
    """
    用户实名认证信息提交时创建审核记录
    """
    # 检查是否是实名认证相关字段的更新
    if hasattr(instance, '_auth_data_submitted'):
        if instance._auth_data_submitted and instance.real_name_auth_status == 'pending':
            UserAuthenticationReview.objects.create(
                user=instance,
                status='pending',
                id_number_snapshot=instance.id_number,
                id_front_image_snapshot=instance.id_front_image,
                id_back_image_snapshot=instance.id_back_image
            )