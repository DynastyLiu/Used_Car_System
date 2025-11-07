from django.contrib import admin
from .models import CarBrand, CarType, Vehicle, VehiclePhoto, VehiclePrice, Review

@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'created_at')

@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vin', 'model_name', 'price', 'status')

admin.site.register(VehiclePhoto)
admin.site.register(VehiclePrice)
admin.site.register(Review)

