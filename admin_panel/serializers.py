from rest_framework import serializers
from .models import AdminLog, SystemStatistics

class AdminLogSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin_user.username', read_only=True)

    class Meta:
        model = AdminLog
        fields = ['id', 'admin_user', 'admin_name', 'operation_type', 'description', 'target_type', 'target_id', 'created_at']

class SystemStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemStatistics
        fields = ['id', 'date', 'total_users', 'total_vehicles', 'total_orders', 'total_revenue', 'active_users']

