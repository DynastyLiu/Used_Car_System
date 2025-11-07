from django.contrib import admin
from .models import User, UserAddress, UserSearchHistory, UserBrowsingHistory

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'user_type', 'account_status', 'created_at')
    list_filter = ('user_type', 'account_status', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone')

admin.site.register(UserAddress)
admin.site.register(UserSearchHistory)
admin.site.register(UserBrowsingHistory)