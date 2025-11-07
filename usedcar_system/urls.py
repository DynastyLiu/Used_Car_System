"""
URL configuration for usedcar_system project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    # Frontend Pages
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('vehicles/', views.vehicles_view, name='vehicles_list'),
    path('vehicles/<int:vehicle_id>/', views.vehicle_detail_view, name='vehicle_detail'),
    path('vehicles/<int:vehicle_id>/edit/', views.edit_vehicle_view, name='edit_vehicle'),
    path('vehicles/publish/', views.publish_vehicle_view, name='publish_vehicle'),
    path('ai-recommend/', views.ai_recommend_view, name='ai_recommend'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('seller-center/', views.seller_center_view, name='seller_center'),
    path('seller/vehicles/', views.seller_vehicles_view, name='seller_vehicles'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('history/', views.history_view, name='history'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('orders/', views.orders_view, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('orders/create/<int:vehicle_id>/', views.create_order_view, name='create_order'),
    path('auth/verification/', views.verification_view, name='verification'),

    # Admin pages
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/vehicle-reviews/', views.admin_vehicle_reviews_view, name='admin_vehicle_reviews'),
    path('admin/user-auth-reviews/', views.admin_user_auth_reviews_view, name='admin_user_auth_reviews'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin/operation-logs/', views.admin_operation_logs_view, name='admin_operation_logs'),

    # Admin Panel
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),

    # Apps URLs
    path('api/users/', include('users.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/admin/', include('admin_panel.urls')),
    path('api/ai/', include('ai_service.urls')),
    path('api/seller/', include('seller.urls')),

    # API endpoints for frontend
    path('api/recent-vehicles/', views.api_recent_vehicles, name='api_recent_vehicles'),
    path('api/featured-brands/', views.api_featured_brands, name='api_featured_brands'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

