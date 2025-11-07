from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from vehicles.models import Vehicle
from .deepseek_service import deepseek
import json
import logging
import re
from decimal import Decimal, InvalidOperation
from django.db.models import Q

logger = logging.getLogger(__name__)


class AIServiceViewSet(viewsets.ViewSet):
    """
    AI服务ViewSet
    """
    permission_classes = [AllowAny]  # 允许所有用户访问，包括未登录用户

    @staticmethod
    def _sanitize_ai_text(text):
        """清理AI返回内容，移除特殊符号并保持整洁换行"""
        if text is None:
            return ''
        if not isinstance(text, str):
            text = str(text)

        cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
        cleaned = re.sub(r'[\\u200b\\u200c\\u200d]', '', cleaned)  # 零宽字符
        cleaned = re.sub(r'[#!*]+', '', cleaned)  # 去除#、!、*

        lines = []
        for raw_line in cleaned.split('\n'):
            line = raw_line.strip()
            if not line:
                lines.append('')
                continue
            # 避免多余空格，保持原有数字编号
            line = re.sub(r'\\s+', ' ', line)
            lines.append(line)

        cleaned_text = '\n'.join(lines).strip()
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        return cleaned_text

    def _build_vehicle_queryset(self, preferences):
        queryset = Vehicle.objects.filter(review_status='approved', status='listed')

        brand_pref = (preferences.get('brand') or '').strip()
        if brand_pref:
            country_mapping = {
                '国产': 'china',
                '进口': 'import',
            }
            mapped_country = country_mapping.get(brand_pref)
            if mapped_country:
                queryset = queryset.filter(brand__country=mapped_country)
            else:
                queryset = queryset.filter(brand__name__icontains=brand_pref)

        car_type_pref = (preferences.get('car_type') or '').strip()
        if car_type_pref:
            queryset = queryset.filter(
                Q(car_type__name__icontains=car_type_pref) |
                Q(description__icontains=car_type_pref)
            )

        price_min = preferences.get('price_min')
        price_max = preferences.get('price_max')

        def to_decimal(value):
            try:
                if value is None or value == '':
                    return None
                return Decimal(str(value))
            except (InvalidOperation, ValueError, TypeError):
                return None

        min_price = to_decimal(price_min)
        max_price = to_decimal(price_max)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        year_min = preferences.get('year_min')
        year_max = preferences.get('year_max')
        try:
            if year_min:
                queryset = queryset.filter(year__gte=int(year_min))
            if year_max:
                queryset = queryset.filter(year__lte=int(year_max))
        except (ValueError, TypeError):
            pass

        detailed = (preferences.get('detailed_requirements') or '').strip()
        if detailed:
            queryset = queryset.filter(Q(description__icontains=detailed))

        return queryset.select_related('brand').prefetch_related('photos')

    @action(detail=False, methods=['post'])
    def vehicle_recommendation(self, request):
        """
        综合车辆推荐
        POST /api/ai/vehicle_recommendation/
        """
        try:
            preferences = request.data.get('preferences') or {}

            ai_raw = deepseek.recommend_vehicles(preferences)
            if not ai_raw:
                return Response({
                    'success': False,
                    'error': 'AI服务暂时不可用，请稍后再试'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            cleaned_text = self._sanitize_ai_text(ai_raw)

            queryset = self._build_vehicle_queryset(preferences)
            vehicles = []

            for vehicle in queryset[:6]:
                main_photo = vehicle.photos.filter(is_main=True).first() or vehicle.photos.first()
                photo_url = None
                if main_photo and getattr(main_photo, 'image', None):
                    try:
                        photo_url = request.build_absolute_uri(main_photo.image.url)
                    except Exception:
                        photo_url = main_photo.image.url

                vehicles.append({
                    'id': vehicle.id,
                    'brand': vehicle.brand.name,
                    'model': vehicle.model_name,
                    'year': vehicle.year,
                    'price': float(vehicle.price),
                    'mileage': vehicle.mileage,
                    'color': vehicle.color,
                    'main_photo': photo_url,
                })

            return Response({
                'success': True,
                'preferences': preferences,
                'ai_recommendations': {
                    'analysis': cleaned_text,
                    'recommendations': cleaned_text,
                },
                'matching_vehicles': vehicles,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"AI vehicle recommendation error: {str(e)}")
            return Response({
                'success': False,
                'error': '获取推荐失败，请稍后再试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def price_estimate(self, request):
        """
        车辆智能定价
        POST /api/ai/price_estimate/
        """
        try:
            vehicle_id = request.data.get('vehicle_id')
            if vehicle_id:
                # 为已有车辆定价
                vehicle = get_object_or_404(Vehicle, id=vehicle_id)
                vehicle_data = {
                    'brand': vehicle.brand.name,
                    'model': vehicle.model_name,
                    'year': vehicle.year,
                    'mileage': vehicle.mileage,
                    'color': vehicle.color,
                    'status': vehicle.status,
                    'description': getattr(vehicle, 'description', '')
                }
            else:
                # 根据输入数据定价
                vehicle_data = request.data.get('vehicle_data', {})

            # 调用DeepSeek API获取价格建议
            ai_result = deepseek.calculate_vehicle_price(vehicle_data)

            if ai_result:
                try:
                    # 尝试解析AI返回的JSON数据
                    price_info = json.loads(ai_result) if ai_result.startswith('{') else {
                        'suggested_price': ai_result,
                        'min_price': None,
                        'max_price': None,
                        'confidence': 0.8,
                        'analysis': ai_result
                    }
                except:
                    price_info = {
                        'suggested_price': ai_result,
                        'min_price': None,
                        'max_price': None,
                        'confidence': 0.7,
                        'analysis': ai_result
                    }

                return Response({
                    'success': True,
                    'vehicle_data': vehicle_data,
                    'price_estimation': price_info,
                    'ai_response': ai_result
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'AI服务暂时不可用，请稍后再试'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.error(f"AI price estimation error: {str(e)}")
            return Response({
                'success': False,
                'error': '定价服务出现错误，请稍后再试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def recommend_vehicles(self, request):
        """
        智能车辆推荐
        POST /api/ai/recommend_vehicles/
        """
        try:
            user_preferences = request.data.get('preferences', {})

            # 调用AI服务获取推荐
            ai_result = deepseek.recommend_vehicles(user_preferences)

            if ai_result:
                return Response({
                    'success': True,
                    'preferences': user_preferences,
                    'recommendations': ai_result
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'AI服务暂时不可用，请稍后再试'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.error(f"AI recommendation error: {str(e)}")
            return Response({
                'success': False,
                'error': '推荐服务出现错误，请稍后再试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def analyze_description(self, request):
        """
        分析车辆描述
        POST /api/ai/analyze_description/
        """
        try:
            description = request.data.get('description', '')

            if not description:
                return Response({
                    'success': False,
                    'error': '请提供车辆描述'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 调用AI服务分析描述
            ai_result = deepseek.analyze_vehicle_description(description)

            if ai_result:
                return Response({
                    'success': True,
                    'description': description,
                    'analysis': ai_result
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'AI服务暂时不可用，请稍后再试'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.error(f"AI description analysis error: {str(e)}")
            return Response({
                'success': False,
                'error': '描述分析服务出现错误，请稍后再试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def chat_assistant(self, request):
        """
        AI聊天助手
        POST /api/ai/chat_assistant/
        """
        try:
            message = request.data.get('message', '')
            conversation_history = request.data.get('conversation_history', [])

            if not message:
                return Response({
                    'success': False,
                    'error': '请输入消息'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 调用AI聊天服务
            ai_response = deepseek.chat_assistant(conversation_history, message)

            if ai_response:
                return Response({
                    'success': True,
                    'message': message,
                    'response': ai_response
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'AI服务暂时不可用，请稍后再试'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.error(f"AI chat assistant error: {str(e)}")
            return Response({
                'success': False,
                'error': '聊天服务出现错误，请稍后再试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
