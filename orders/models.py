from django.db import models
from users.models import User
from vehicles.models import Vehicle

class Order(models.Model):
    STATUS_CHOICES = (('pending_payment', 'Pending Payment'), ('paid', 'Paid'), ('trading', 'Trading'), ('completed', 'Completed'), ('cancelled', 'Cancelled'))

    order_number = models.CharField(max_length=100, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_seller')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    buyer_note = models.TextField(blank=True)
    seller_note = models.TextField(blank=True)

    # 新增购买相关字段
    buyer_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='买家电话')
    delivery_address = models.TextField(null=True, blank=True, verbose_name='配送地址')
    delivery_time = models.DateTimeField(null=True, blank=True, verbose_name='期望送达时间')
    vehicle_color = models.CharField(max_length=50, null=True, blank=True, verbose_name='车辆颜色')
    vehicle_model_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='车辆款型')

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']

class OrderMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=(('text', 'Text'), ('image', 'Image'), ('file', 'File')))
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders_message'

class OrderReview(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    content = models.TextField()
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders_review'

class OrderPayment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=(('alipay', 'Alipay'), ('wechat', 'WeChat'), ('bank_transfer', 'Bank Transfer')))
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')))
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders_payment'

