from django.contrib import admin
from .models import AdminLog, SystemStatistics

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'operation_type', 'target_type', 'created_at')
    list_filter = ('operation_type', 'created_at')
    search_fields = ('admin_user__username', 'operation_type')

admin.site.register(SystemStatistics)

