"""
主应用视图
用于处理前端页面渲染
"""
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework import status
from vehicles.models import Vehicle, CarBrand
from vehicles.serializers import VehicleSerializer

logger = logging.getLogger(__name__)


def home_view(request):
    """
    首页视图 - 检查用户登录状态
    """
    # 如果用户已登录，重定向到仪表板
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        # 如果未登录，显示登录注册页面
        return render(request, 'auth/landing.html')


def dashboard_view(request):
    """
    用户仪表板页面 - 登录后的首页
    """
    return render(request, 'dashboard.html')


def profile_view(request):
    """
    个人中心页面
    """
    return render(request, 'profile.html')


def settings_view(request):
    """
    账户设置页面
    """
    return render(request, 'settings.html')


def logout_view(request):
    """
    用户登出视图
    """
    # 清除本地存储的token
    from django.contrib.auth import logout
    logout(request)

    # 返回JSON响应用于AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'message': '登出成功', 'redirect': '/'})

    # 普通请求重定向到首页
    return redirect('home')


def vehicles_view(request):
    """
    车辆列表页面
    """
    return render(request, 'vehicles/list.html')


def vehicle_detail_view(request, vehicle_id):
    """
    车辆详情页面
    """
    return render(request, 'vehicles/detail.html', {'vehicle_id': vehicle_id})


def ai_recommend_view(request):
    """
    AI推荐页面
    """
    return render(request, 'ai/recommend.html')


def about_view(request):
    """
    关于我们页面
    """
    return render(request, 'about.html')


def contact_view(request):
    """
    联系我们页面
    """
    return render(request, 'contact.html')


def seller_center_view(request):
    """
    卖家中心页面
    """
    return render(request, 'seller/index.html')


def publish_vehicle_view(request):
    """
    发布车辆页面
    """
    return render(request, 'vehicles/publish.html')


def edit_vehicle_view(request, vehicle_id):
    """
    编辑车辆页面
    """
    return render(request, 'vehicles/edit_vehicle.html', {'vehicle_id': vehicle_id})


def seller_vehicles_view(request):
    """
    我的车辆页面
    """
    return render(request, 'seller/vehicles.html')


def favorites_view(request):
    """
    我的收藏页面
    """
    return render(request, 'favorites.html')


def wallet_view(request):
    """
    钱包页面
    """
    return render(request, 'wallet.html')


def history_view(request):
    """
    浏览历史页面
    """
    return render(request, 'history.html')


def orders_view(request):
    """
    订单列表页面
    """
    return render(request, 'orders/list.html')


def order_detail_view(request, order_id):
    """
    订单详情页面
    """
    return render(request, 'orders/detail.html', {'order_id': order_id})


def create_order_view(request, vehicle_id):
    """
    创建订单页面
    获取钱包信息 - 尝试从JWT token或session中认证用户
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from rest_framework.request import Request as DRFRequest

    # 获取钱包信息
    wallet_info = {
        'balance': 0.0,
        'has_payment_password': False,
        'is_authenticated': request.user.is_authenticated
    }

      
    # 首先检查是否已经通过session认证
    user = None
    if request.user.is_authenticated:
        user = request.user
    else:
        # 尝试从Authorization header中提取JWT token进行认证
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            logger.debug("尝试从Authorization header中认证用户")
            try:
                jwt_auth = JWTAuthentication()
                drf_request = DRFRequest(request)
                auth_result = jwt_auth.authenticate(drf_request)

                if auth_result is not None:
                    user, validated_token = auth_result
                    request.user = user
                    request.auth = validated_token
                    logger.debug(f"用户已通过JWT认证: {user.username}")
                else:
                    logger.debug("JWT认证返回None")
            except (InvalidToken, TokenError) as e:
                logger.debug(f"JWT认证失败: {e}")
        else:
            logger.debug("没有Authorization header")

    # 如果成功认证用户，获取钱包信息
    if user and user.is_authenticated:
        try:
            # 获取用户的钱包余额
            user_profile = user.profile
            wallet_info['balance'] = float(user_profile.balance)
            wallet_info['has_payment_password'] = bool(user.payment_password)
            wallet_info['is_authenticated'] = True
            logger.debug(f"wallet_info updated: balance={wallet_info['balance']}, password_set={wallet_info['has_payment_password']}")
        except Exception as e:
            # 如果获取失败，使用默认值
            logger.debug(f"获取钱包信息失败: {e}")
    else:
        logger.debug("用户未认证，使用默认钱包信息")

    return render(request, 'orders/create.html', {
        'vehicle_id': vehicle_id,
        'wallet_info': wallet_info
    })


def verification_view(request):
    """
    实名认证页面
    """
    return render(request, 'auth/verification.html')


def admin_dashboard_view(request):
    """
    管理员仪表板页面
    """
    return render(request, 'admin/dashboard.html')


def admin_vehicle_reviews_view(request):
    """
    车辆审核页面
    """
    return render(request, 'admin/vehicle_reviews.html')


def admin_user_auth_reviews_view(request):
    """
    用户认证审核页面
    """
    return render(request, 'admin/user_auth_reviews.html')


def admin_reports_view(request):
    """
    举报管理页面
    """
    return render(request, 'admin/reports.html')


def admin_operation_logs_view(request):
    """
    操作日志页面
    """
    return render(request, 'admin/operation_logs.html')


# API视图用于前端JavaScript调用
def api_recent_vehicles(request):
    """
    获取最近发布的车辆列表API
    """
    try:
        vehicles = Vehicle.objects.filter(status='available')[:8]
        serializer = VehicleSerializer(vehicles, many=True)
        return JsonResponse({
            'success': True,
            'results': serializer.data,
            'count': vehicles.count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def api_featured_brands(request):
    """
    获取热门品牌列表API
    """
    try:
        brands = CarBrand.objects.filter(is_active=True)[:8]
        return JsonResponse({
            'success': True,
            'results': list(brands.values('id', 'name', 'country'))
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)