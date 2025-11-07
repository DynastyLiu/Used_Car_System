"""
用户模块视图和ViewSets
"""
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
import logging

from .models import User, UserProfile, UserAddress, UserLoginHistory, UserOperationLog, UserBrowsingHistory, WalletTransaction
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    UserAddressSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    UserRealNameAuthSerializer,
    UserSellerAuthSerializer,
    UserLoginHistorySerializer,
    UserBrowsingHistorySerializer,
    WalletTransactionSerializer,
    WalletInfoSerializer,
)
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal

logger = logging.getLogger(__name__)


class UserRegistrationView(CreateAPIView):
    """
    用户注册视图
    POST /api/users/register/
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """重写create方法以添加操作日志"""
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            logger.info(f"用户注册成功: {response.data.get('username')}")

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义登录视图
    POST /api/users/login/
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """重写post方法以添加登录历史记录"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, serializers.ValidationError) as exc:
            # 记录登录失败
            self._record_failed_login(request)
            logger.error("登录失败: %s", exc)

            # 抛出合适的异常
            if isinstance(exc, TokenError):
                raise InvalidToken(exc.args[0])
            else:
                # ValidationError已经是正确的格式，直接re-raise
                raise

        # 获取认证后的用户对象（从serializer中保存的）
        user = getattr(serializer, 'user', None)
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        # 记录登录成功历史
        if user:
            self._record_successful_login(user, request)
        else:
            # 即使user为None，也记录失败登录（这不应该发生，但以防万一）
            self._record_failed_login(request)
            logger.warning("登录成功但无法获取用户对象")

        return response

    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _resolve_user(self, identifier):
        if not identifier:
            return None
        return User.objects.filter(
            Q(username=identifier) |
            Q(email=identifier) |
            Q(phone=identifier)
        ).first()

    def _record_successful_login(self, user, request):
        UserLoginHistory.objects.create(
            user=user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True
        )

        user.login_count = (user.login_count or 0) + 1
        user.last_login_ip = self.get_client_ip(request)
        user.save(update_fields=['login_count', 'last_login_ip'])
        logger.info("用户登录成功: %s", user.username)

    def _record_failed_login(self, request):
        identifier = request.data.get('username')
        user = self._resolve_user(identifier)

        if not user:
            return

        user.failed_login_count = (user.failed_login_count or 0) + 1
        user.last_failed_login = timezone.now()
        user.save(update_fields=['failed_login_count', 'last_failed_login'])

        UserLoginHistory.objects.create(
            user=user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False
        )


class UserProfileView(RetrieveUpdateAPIView):
    """
    用户资料视图
    GET/PUT/PATCH /api/users/profile/
    """
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserAddressViewSet(viewsets.ModelViewSet):
    """
    用户地址管理
    """
    serializer_class = UserAddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PasswordChangeView(APIView):
    """
    修改密码视图
    POST /api/users/change-password/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '密码修改成功'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRealNameAuthView(APIView):
    """
    用户实名认证视图
    POST /api/users/real-name-auth/
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        user = request.user
        data = {
            'real_name_auth_status': user.real_name_auth_status or 'unverified',
            'id_number': user.id_number,
            'id_front_image': request.build_absolute_uri(user.id_front_image.url) if user.id_front_image else None,
            'id_back_image': request.build_absolute_uri(user.id_back_image.url) if user.id_back_image else None,
            'bank_account_name': user.bank_account_name,
            'bank_card_number': user.bank_card_number,
            'bank_name': user.bank_name,
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserRealNameAuthSerializer(
            data=request.data,
            instance=request.user,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': '实名认证信息提交成功，请等待审核',
                    'real_name_auth_status': request.user.real_name_auth_status
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSellerAuthView(APIView):
    """
    用户卖家认证视图
    POST /api/users/seller-auth/
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        user = request.user
        data = {
            'bank_account_name': user.bank_account_name,
            'bank_card_number': user.bank_card_number,
            'bank_name': user.bank_name,
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSellerAuthSerializer(
            data=request.data,
            instance=request.user,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '卖家认证信息提交成功，请等待审核'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """
    用户统计信息视图
    GET /api/users/stats/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = user.profile

        stats = {
            'total_purchases': profile.total_purchases,
            'total_sales': profile.total_sales,
            'average_rating': profile.average_rating,
            'total_reviews': profile.total_reviews,
            'balance': float(profile.balance),
            'published_vehicles': user.vehicles.filter(status='listed').count(),
            'sold_vehicles': user.vehicles.filter(status='sold').count(),
            'pending_orders': user.orders_as_seller.filter(status='pending_payment').count() | \
                           user.orders_as_buyer.filter(status='pending_payment').count(),
        }

        return Response(stats)


class UserBrowsingHistoryViewSet(viewsets.ModelViewSet):
    """
    用户浏览历史ViewSet
    GET /api/users/browsing-history/ - 获取当前用户的浏览历史（按时间降序）
    POST /api/users/browsing-history/ - 记录一条浏览历史
    """
    serializer_class = UserBrowsingHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """只返回当前用户的浏览历史，按浏览时间降序排列"""
        return UserBrowsingHistory.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-browse_time')

    def perform_create(self, serializer):
        """创建浏览记录时自动关联当前用户"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """记录浏览历史"""
        vehicle_id = request.data.get('vehicle_id')

        if not vehicle_id:
            return Response(
                {'error': '缺少vehicle_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否已存在相同车辆的浏览记录
        existing_record = UserBrowsingHistory.objects.filter(
            user=request.user,
            vehicle_id=vehicle_id
        ).first()

        if existing_record:
            # 如果已存在，更新浏览时间
            existing_record.browse_time = timezone.now()
            existing_record.save()
            serializer = self.get_serializer(existing_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # 如果不存在，创建新记录
            return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """获取浏览历史列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        """清除当前用户的所有浏览历史"""
        deleted_count = UserBrowsingHistory.objects.filter(
            user=request.user
        ).delete()[0]

        return Response(
            {
                'message': '浏览历史已全部清除',
                'deleted_count': deleted_count
            },
            status=status.HTTP_200_OK
        )


class WalletView(APIView):
    """
    钱包视图
    GET /api/users/wallet/ - 获取钱包信息
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """获取钱包信息"""
        user = request.user

        # 确保用户有关联的UserProfile,如果没有则创建
        try:
            profile = user.profile
        except:
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)

        data = {
            'balance': float(profile.balance),
            'frozen_balance': float(profile.frozen_balance),
            'has_payment_password': user.payment_password is not None and user.payment_password != ''
        }

        return Response(data, status=status.HTTP_200_OK)


class SetPaymentPasswordView(APIView):
    """
    设置交易密码视图
    POST /api/users/set-payment-password/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """设置6位数字交易密码"""
        user = request.user
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')

        # 验证密码
        if not password or not password_confirm:
            return Response(
                {'error': '密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证是否为6位数字
        if len(password) != 6 or not password.isdigit():
            return Response(
                {'error': '密码必须是6位数字'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证两次密码是否一致
        if password != password_confirm:
            return Response(
                {'error': '两次输入的密码不一致'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否已设置密码
        if user.payment_password:
            return Response(
                {'error': '您已设置过交易密码，如需修改请联系客服'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 保存密码（加密）
        user.payment_password = make_password(password)
        user.save()

        return Response(
            {'message': '交易密码设置成功'},
            status=status.HTTP_200_OK
        )


class ChangePaymentPasswordView(APIView):
    """
    修改交易密码视图
    POST /api/users/change-payment-password/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """修改6位数字交易密码"""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')

        # 验证输入
        if not current_password or not new_password or not confirm_new_password:
            return Response(
                {'error': '请填写所有密码字段'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证密码格式
        if len(current_password) != 6 or not current_password.isdigit():
            return Response(
                {'error': '当前密码必须是6位数字'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) != 6 or not new_password.isdigit():
            return Response(
                {'error': '新密码必须是6位数字'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(confirm_new_password) != 6 or not confirm_new_password.isdigit():
            return Response(
                {'error': '确认新密码必须是6位数字'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否已设置密码
        if not user.payment_password:
            return Response(
                {'error': '您还未设置交易密码，请先设置'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证当前密码是否正确
        if not check_password(current_password, user.payment_password):
            return Response(
                {'error': '当前密码不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证新密码不能与当前密码相同
        if current_password == new_password:
            return Response(
                {'error': '新密码不能与当前密码相同'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证两次输入的新密码是否一致
        if new_password != confirm_new_password:
            return Response(
                {'error': '两次输入的新密码不一致'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新密码（加密）
        user.payment_password = make_password(new_password)
        user.save()

        return Response(
            {'message': '交易密码修改成功'},
            status=status.HTTP_200_OK
        )


class VerifyPaymentPasswordView(APIView):
    """
    验证交易密码视图
    POST /api/users/verify-payment-password/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """验证交易密码"""
        user = request.user
        password = request.data.get('password')

        if not password:
            return Response(
                {'error': '密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.payment_password:
            return Response(
                {'error': '您还未设置交易密码'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证密码
        if check_password(password, user.payment_password):
            return Response(
                {'message': '密码验证成功', 'verified': True},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': '密码错误', 'verified': False},
                status=status.HTTP_401_UNAUTHORIZED
            )


class WalletRechargeView(APIView):
    """
    充值视图
    POST /api/users/wallet/recharge/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """充值金额"""
        user = request.user

        # 确保用户有关联的UserProfile,如果没有则创建
        try:
            profile = user.profile
        except:
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)

        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        payment_password = request.data.get('payment_password')

        # 验证参数
        if not amount or not payment_method or not payment_password:
            return Response(
                {'error': '参数不完整'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证支付方式
        valid_methods = ['wechat', 'alipay', 'bank']
        if payment_method not in valid_methods:
            return Response(
                {'error': '支付方式无效'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证金额
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': '金额必须大于0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证交易密码
        if not user.payment_password:
            return Response(
                {'error': '请先设置交易密码'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(payment_password, user.payment_password):
            return Response(
                {'error': '交易密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 执行充值（使用事务）
        from django.db import transaction
        try:
            with transaction.atomic():
                # 更新余额
                profile.balance += amount
                profile.save()

                # 创建交易记录
                WalletTransaction.objects.create(
                    user=user,
                    amount=amount,
                    transaction_type='recharge',
                    payment_method=payment_method,
                    status='success',
                    description=f'通过{dict(WalletTransaction.PAYMENT_METHOD_CHOICES)[payment_method]}充值'
                )

            return Response(
                {
                    'message': '充值成功',
                    'new_balance': float(profile.balance),
                    'amount': float(amount)
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"充值失败: {str(e)}")
            return Response(
                {'error': '充值失败，请重试'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletTransactionListView(APIView):
    """
    交易记录列表视图
    GET /api/users/wallet/transactions/
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """获取交易记录"""
        user = request.user
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 20

        # 获取交易记录
        queryset = WalletTransaction.objects.filter(user=user).order_by('-created_at')
        total = queryset.count()

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        transactions = queryset[start:end]

        serializer = WalletTransactionSerializer(transactions, many=True)

        return Response(
            {
                'results': serializer.data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            },
            status=status.HTTP_200_OK
        )
