from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'addresses', views.UserAddressViewSet, basename='address')
router.register(r'browsing-history', views.UserBrowsingHistoryViewSet, basename='browsing-history')

urlpatterns = [
    # 用户认证相关
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),

    # 密码相关
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),

    # 实名认证
    path('real-name-auth/', views.UserRealNameAuthView.as_view(), name='real_name_auth'),

    # 卖家认证
    path('seller-auth/', views.UserSellerAuthView.as_view(), name='seller_auth'),

    # 用户统计
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),

    # 钱包相关
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('set-payment-password/', views.SetPaymentPasswordView.as_view(), name='set_payment_password'),
    path('change-payment-password/', views.ChangePaymentPasswordView.as_view(), name='change_payment_password'),
    path('verify-payment-password/', views.VerifyPaymentPasswordView.as_view(), name='verify_payment_password'),
    path('wallet/recharge/', views.WalletRechargeView.as_view(), name='wallet_recharge'),
    path('wallet/transactions/', views.WalletTransactionListView.as_view(), name='wallet_transactions'),

    # 其他路由
    path('', include(router.urls))
]