from django.db import models
from users.models import User
from vehicles.models import Vehicle

class AdminLog(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    operation_type = models.CharField(max_length=50)
    description = models.TextField()
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_log'

class SystemStatistics(models.Model):
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    total_vehicles = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active_users = models.IntegerField(default=0)

    class Meta:
        db_table = 'admin_statistics'

