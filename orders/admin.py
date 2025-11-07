from django.contrib import admin
from .models import Order, OrderMessage, OrderReview, OrderPayment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'seller', 'vehicle', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'buyer__username', 'seller__username')

admin.site.register(OrderMessage)
admin.site.register(OrderReview)
admin.site.register(OrderPayment)

