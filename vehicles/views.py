from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from django.utils import timezone
from django.http import QueryDict
import uuid
import json
from datetime import date
from .models import CarBrand, CarType, Vehicle, VehiclePhoto, VehiclePrice, Review, Favorite
from .serializers import (
    CarBrandSerializer, CarTypeSerializer, VehicleSerializer,
    VehicleCreateSerializer, VehiclePhotoSerializer, VehiclePriceSerializer,
    ReviewSerializer, FavoriteSerializer
)

class CarBrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    permission_classes = [AllowAny]
    search_fields = ['name', 'country']

class CarTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarType.objects.all()
    serializer_class = CarTypeSerializer
    permission_classes = [AllowAny]

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    search_fields = ['model_name', 'brand__name', 'car_type__name', 'description', 'vin']
    ordering_fields = ['price', 'created_at', 'mileage']

    def get_serializer_class(self):
        """Return the serializer class based on the current action"""
        if self.action in ['create', 'update', 'partial_update']:
            return VehicleCreateSerializer
        return VehicleSerializer

    def get_permissions(self):
        """设置权限：查看允许任何人，创建和编辑需要登录和权限"""
        # 对于以下操作需要认证：
        # 1. my_vehicles端点的任何操作
        # 2. 创建车辆
        # 3. 更新、部分更新、删除车辆
        if (self.request.path.endswith("/my_vehicles/") or
            self.action in ['create', 'update', 'partial_update', 'destroy']):
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_update(self, serializer):
        """确保只有车辆所有者可以编辑"""
        vehicle = self.get_object()
        if vehicle.seller != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限编辑此车辆")
        serializer.save()

    def perform_destroy(self, instance):
        """确保只有车辆所有者可以删除"""
        if instance.seller != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您没有权限删除此车辆")
        instance.delete()

    def _prepare_vehicle_payload(self, request):
        """
        Normalize incoming data so that simplified seller forms can be accepted.
        """
        raw_data = request.data
        if isinstance(raw_data, QueryDict):
            data = {key: raw_data.get(key) for key in raw_data.keys()}
            images = raw_data.getlist('images')
        else:
            data = dict(raw_data)
            images = data.get('images') or []

        model_value = data.pop('model', None)
        if model_value and not data.get('model_name'):
            data['model_name'] = model_value

        if data.get('car_type') in (None, '', 'null'):
            data['car_type'] = None

        mileage = data.get('mileage')
        if mileage in (None, '', 'null'):
            data['mileage'] = 0

        if not data.get('description'):
            data['description'] = 'Description not provided by seller.'

        highlights = data.get('highlights')
        if not highlights:
            data['highlights'] = []
        elif isinstance(highlights, str):
            try:
                parsed = json.loads(highlights)
                data['highlights'] = parsed if isinstance(parsed, list) else [highlights]
            except json.JSONDecodeError:
                data['highlights'] = [item.strip() for item in highlights.split(',') if item.strip()]

        if not data.get('vin'):
            data['vin'] = f"AUTO-{uuid.uuid4().hex[:12].upper()}"

        defaults = {
            'color': 'Not specified',
            'transmission': 'auto',
            'emission_standard': 'euro5',
            'fuel_type': 'gasoline',
        }
        for field, default in defaults.items():
            if not data.get(field):
                data[field] = default

        if not data.get('plate_date'):
            year_value = data.get('year')
            try:
                year_int = int(year_value)
                data['plate_date'] = date(year_int, 1, 1).isoformat()
            except (TypeError, ValueError):
                data['plate_date'] = timezone.now().date().isoformat()

        if not data.get('first_owner_date'):
            data['first_owner_date'] = None

        price = data.get('price')
        if price in (None, '', 'null'):
            data['price'] = '0'

        year_value = data.get('year')
        if year_value in (None, '', 'null'):
            data['year'] = timezone.now().year

        data['images'] = images or []

        return data

    def create(self, request, *args, **kwargs):
        data = self._prepare_vehicle_payload(request)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Attach the current user as seller when creating a vehicle"""
        serializer.save(
            seller=self.request.user,
            status='pending_review',
            review_status='pending'
        )

    def get_queryset(self):
        """Return vehicles for public listings or seller-specific management."""
        request = self.request
        user = request.user
        is_seller_context = request.path.startswith("/api/seller/") or request.path.endswith("/my_vehicles/")

        if is_seller_context:
            if not user.is_authenticated:
                return Vehicle.objects.none()
            queryset = Vehicle.objects.filter(seller=user)
            status_filter = request.query_params.get("status")
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        else:
            queryset = Vehicle.objects.filter(review_status="approved", status="listed")

        brand_id = request.query_params.get("brand")
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        year_min = request.query_params.get("year_min")
        year_max = request.query_params.get("year_max")
        if year_min:
            queryset = queryset.filter(year__gte=year_min)
        if year_max:
            queryset = queryset.filter(year__lte=year_max)

        search_query = request.query_params.get("search")
        if search_query:
            search_query = search_query.strip()
            if search_query:
                queryset = queryset.filter(
                    Q(model_name__icontains=search_query) |
                    Q(brand__name__icontains=search_query) |
                    Q(car_type__name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(vin__icontains=search_query)
                )

        return queryset.select_related("brand", "car_type", "seller").prefetch_related("photos").order_by("-created_at")

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Toggle favorite status for the current user"""
        vehicle = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'Please sign in first'}, status=status.HTTP_401_UNAUTHORIZED)

        favorite, created = Favorite.objects.get_or_create(user=user, vehicle=vehicle)

        if created:
            return Response({'message': 'Favorite added'})

        favorite.delete()
        return Response({'message': 'Favorite removed'})

    @action(detail=False, methods=['get', 'post', 'put', 'patch'])
    def my_vehicles(self, request):
        """获取或创建当前用户的车辆"""
        if request.method == 'GET':
            # 获取当前用户的车辆列表
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            # 创建新车辆，复用create方法
            return self.create(request)

        # 对于PUT/PATCH，需���具体的车辆ID，这里不处理
        return Response({'error': 'Method not allowed for this endpoint'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """鑾峰彇杞﹁締鐓х墖"""
        vehicle = self.get_object()
        photos = vehicle.photos.all().order_by('order')
        serializer = VehiclePhotoSerializer(photos, many=True)
        return Response(serializer.data)

class VehiclePhotoViewSet(viewsets.ModelViewSet):
    serializer_class = VehiclePhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VehiclePhoto.objects.filter(vehicle_id=self.kwargs['vehicle_pk'])

    def perform_create(self, serializer):
        serializer.save(vehicle_id=self.kwargs['vehicle_pk'])


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(vehicle_id=self.kwargs['vehicle_pk'])

    def perform_create(self, serializer):
        serializer.save(
            reviewer=self.request.user,
            vehicle_id=self.kwargs['vehicle_pk']
        )


class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user, is_active=True)
