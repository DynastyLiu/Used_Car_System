"""
车辆图片搜索功能
使用Unsplash API搜索真实车辆图片
"""

import os
import requests
from PIL import Image
import io
import random
from django.conf import settings
from pathlib import Path

class VehicleImageSearcher:
    def __init__(self):
        self.unsplash_access_key = 'YOUR_UNSPLASH_ACCESS_KEY'  # 需要替换为真实的Unsplash API密钥
        self.base_path = Path(settings.MEDIA_ROOT) / 'vehicle_images'
        self.base_path.mkdir(parents=True, exist_ok=True)

        # 车辆相关的搜索关键词
        self.vehicle_keywords = [
            'car', 'automobile', 'sedan', 'SUV', 'truck', 'sports car',
            'luxury car', 'vintage car', 'electric car', 'hybrid car'
        ]

    def search_vehicle_images(self, brand_name, model_name, count=5):
        """
        搜索车辆图片

        Args:
            brand_name (str): 品牌名称
            model_name (str): 车型名称
            count (int): 搜索图片数量

        Returns:
            list: 图片URL列表
        """
        # 构建搜索查询
        search_query = f"{brand_name} {model_name}"

        # 使用Unsplash API搜索
        headers = {
            'Authorization': f'Client-ID {self.unsplash_access_key}'
        }

        params = {
            'query': search_query,
            'per_page': min(count, 30),
            'orientation': 'horizontal',
            'color': 'any',
            'content_filter': 'high'
        }

        try:
            response = requests.get(
                'https://api.unsplash.com/search/photos',
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return [photo['urls']['regular'] for photo in data.get('results', [])]
            else:
                print(f"Unsplash API请求失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"搜索车辆图片失败: {e}")
            return []

    def download_vehicle_image(self, image_url, brand_name, model_name):
        """
        下载车辆图片

        Args:
            image_url (str): 图片URL
            brand_name (str): 品牌名称
            model_name (str): 车型名称

        Returns:
            str: 保存的文件路径
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # 使用PIL处理图片
            image = Image.open(io.BytesIO(response.content))

            # 转换为RGB模式
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # 调整图片大小
            image.thumbnail((800, 600), Image.Resampling.LANCZOS)

            # 生成文件名
            safe_brand = "".join(c for c in brand_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_model = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_brand}_{safe_model}_{random.randint(1000, 9999)}.jpg"

            # 保存文件
            file_path = self.base_path / filename
            image.save(file_path, 'JPEG', quality=90, optimize=True)

            return f'vehicle_images/{filename}'

        except Exception as e:
            print(f"下载车辆图片失败 {image_url}: {e}")
            return None

    def get_placeholder_images(self, brand_name, model_name):
        """
        获取占位符图片URL

        Args:
            brand_name (str): 品牌名称
            model_name (str): 车型名称

        Returns:
            list: 占位符图片URL列表
        """
        # 使用在线占位符服务
        return [
            f"https://via.placeholder.com/800x600/4A90E2/FFFFFF?text={brand_name}+{model_name}",
            f"https://picsum.photos/800/600?random={random.randint(1000, 9999)}",
            f"https://dummyimage.com/800x600/4A90E2/FFFFFF&text={brand_name}+{model_name}"
        ]

def create_sample_vehicle_images():
    """
    创建示例车辆图片
    """
    from vehicles.models import Vehicle, VehiclePhoto
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # 获取所有车辆
    vehicles = Vehicle.objects.filter(review_status='approved', status='sale')[:10]

    searcher = VehicleImageSearcher()

    for vehicle in vehicles:
        print(f"正在为车辆 {vehicle.brand.name} {vehicle.model_name} 搜索图片...")

        # 搜索图片
        image_urls = searcher.search_vehicle_images(
            vehicle.brand.name,
            vehicle.model_name,
            count=3
        )

        if image_urls:
            # 下载第一张图片作为主图
            main_image_path = searcher.download_vehicle_image(
                image_urls[0],
                vehicle.brand.name,
                vehicle.model_name
            )

            if main_image_path:
                # 创建车辆图片记录
                VehiclePhoto.objects.create(
                    vehicle=vehicle,
                    image=main_image_path,
                    is_main=True,
                    order=0
                )
                print(f"成功下载主图: {main_image_path}")

            # 下载其他图片
            for i, url in enumerate(image_urls[1:], 1):
                image_path = searcher.download_vehicle_image(
                    url,
                    vehicle.brand.name,
                    vehicle.model_name
                )

                if image_path:
                    VehiclePhoto.objects.create(
                        vehicle=vehicle,
                        image=image_path,
                        is_main=False,
                        order=i
                    )
                    print(f"成功下载图片: {image_path}")

        else:
            # 使用占位符图片
            placeholder_urls = searcher.get_placeholder_images(
                vehicle.brand.name,
                vehicle.model_name
            )

            for i, url in enumerate(placeholder_urls):
                image_path = searcher.download_vehicle_image(
                    url,
                    vehicle.brand.name,
                    vehicle.model_name
                )

                if image_path:
                    VehiclePhoto.objects.create(
                        vehicle=vehicle,
                        image=image_path,
                        is_main=(i == 0),
                        order=i
                    )
                    print(f"使用占位符图片: {image_path}")

        # 暂时避免请求过快
        import time
        time.sleep(1)

if __name__ == '__main__':
    create_sample_vehicle_images()