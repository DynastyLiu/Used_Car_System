from rest_framework import serializers
from .models import CarBrand, CarType, Vehicle, VehiclePhoto, VehiclePrice, Review, Favorite

class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ['id', 'name', 'logo', 'country']

class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = ['id', 'name', 'parent']

class VehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhoto
        fields = ['id', 'image', 'is_main', 'order']

class VehiclePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePrice
        fields = ['suggested_price', 'min_price', 'max_price', 'confidence_score']

class VehicleSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    car_type_name = serializers.CharField(source='car_type.name', read_only=True)
    photos = VehiclePhotoSerializer(many=True, read_only=True)
    price_info = VehiclePriceSerializer(read_only=True, allow_null=True)
    main_photo = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'vin',
            'brand',
            'brand_name',
            'car_type',
            'car_type_name',
            'model_name',
            'year',
            'color',
            'transmission',
            'fuel_type',
            'emission_standard',
            'mileage',
            'plate_date',
            'first_owner_date',
            'description',
            'highlights',
            'price',
            'status',
            'status_display',
            'review_status',
            'view_count',
            'favorite_count',
            'main_photo',
            'photos',
            'price_info',
            'seller',
            'created_at',
            'updated_at',
        ]

    def get_main_photo(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        photo = obj.photos.filter(is_main=True).first() or obj.photos.first()
        if not photo or not getattr(photo, 'image', None):
            return None
        url = photo.image.url
        if request:
            try:
                return request.build_absolute_uri(url)
            except Exception:
                return url
        return url

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'content', 'reviewer', 'reviewer_name', 'created_at']


class VehicleCreateSerializer(serializers.ModelSerializer):
    """杞﹁締鍒涘缓搴忓垪鍖栧櫒"""
    # 鏀寔澶氬浘鐗囦笂浼?
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Vehicle
        fields = [
            'vin', 'brand', 'car_type', 'model_name', 'year', 'color',
            'transmission', 'emission_standard', 'fuel_type', 'mileage',
            'plate_date', 'first_owner_date', 'description', 'highlights', 'price',
            'images'
        ]
        extra_kwargs = {
            'seller': {'read_only': True}
        }

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])

        validated_data["seller"] = self.context["request"].user
        validated_data.setdefault("status", "pending_review")
        validated_data.setdefault("review_status", "pending")

        vehicle = super().create(validated_data)

        for index, image in enumerate(images_data):
            VehiclePhoto.objects.create(
                vehicle=vehicle,
                image=image,
                order=index,
                is_main=(index == 0)
            )

        VehiclePrice.objects.update_or_create(
            vehicle=vehicle,
            defaults={
                "suggested_price": vehicle.price,
                "min_price": vehicle.price,
                "max_price": vehicle.price,
                "confidence_score": 0.8,
            }
        )

        return vehicle

    def update(self, instance, validated_data):
        """更新车辆信息"""
        images_data = validated_data.pop("images", [])

        # 更新车辆基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # 处理图片更新
        if images_data:
            # 删除旧图片（可选，或者根据前端传来的删除列表）
            # instance.photos.all().delete()

            # 添加新图片
            for index, image in enumerate(images_data):
                VehiclePhoto.objects.create(
                    vehicle=instance,
                    image=image,
                    order=instance.photos.count() + index,
                    is_main=False  # 更新时不自动设为主图
                )

        # 更新价格信息
        VehiclePrice.objects.update_or_create(
            vehicle=instance,
            defaults={
                "suggested_price": instance.price,
                "min_price": instance.price,
                "max_price": instance.price,
                "confidence_score": 0.8,
            }
        )

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """鏀惰棌搴忓垪鍖栧櫒"""
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'vehicle', 'vehicle_info', 'is_active', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_vehicle_info(self, obj):
        vehicle = obj.vehicle
        main_photo = vehicle.photos.filter(is_main=True).first()
        return {
            'id': vehicle.id,
            'vin': vehicle.vin,
            'brand_name': vehicle.brand.name,
            'model_name': vehicle.model_name,
            'year': vehicle.year,
            'price': vehicle.price,
            'main_photo': main_photo.image.url if main_photo else None,
            'status': vehicle.status,
            'mileage': vehicle.mileage,
            'view_count': vehicle.view_count
        }

