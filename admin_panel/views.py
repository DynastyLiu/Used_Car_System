from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import AdminLog, SystemStatistics
from .serializers import AdminLogSerializer, SystemStatisticsSerializer
from users.models import User
from vehicles.models import Vehicle
from orders.models import Order

class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated]

class SystemStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemStatistics.objects.all()
    serializer_class = SystemStatisticsSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        today = timezone.now().date()
        stats = {
            'total_users': User.objects.count(),
            'total_vehicles': Vehicle.objects.count(),
            'total_orders': Order.objects.count(),
            'today_orders': Order.objects.filter(created_at__date=today).count(),
            'pending_reviews': Vehicle.objects.filter(review_status='pending').count(),
        }
        return Response(stats)

