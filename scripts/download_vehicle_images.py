#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动为车辆下载网络图片的脚本
使用Bing Image Search API下载车辆和品牌标志图片
"""

import os
import sys
import django
import requests
import time
from datetime import datetime
from pathlib import Path

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'usedcar_system.settings')
django.setup()

from vehicles.models import Vehicle, VehiclePhoto, CarBrand

# 配置参数
MEDIA_ROOT = Path('/static') / 'images' / 'vehicles'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def download_image(url, save_path):
    """从URL下载图片并保存"""
    try:
        response = requests.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=10,
            verify=False
        )

        if response.status_code == 200:
            # 创建目录
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(response.content)

            print(f'✓ 下载成功: {save_path.name}')
            return True
    except Exception as e:
        print(f'✗ 下载失败: {url} - {str(e)}')

    return False

def search_and_download_vehicle_image(vehicle, image_number=1):
    """为车辆搜索并下载图片"""
    try:
        # 构建搜索关键词
        search_query = f'{vehicle.brand.name} {vehicle.model_name} {vehicle.year} car'

        # 使用Google或Bing的图片搜索
        # 这里使用一个简化的方法 - 直接从常见的汽车图片网站下载
        search_url = f'https://www.bing.com/images/search?q={search_query.replace(" ", "+")}'

        print(f'搜索: {search_query}')

        # 尝试多个备用图片来源
        image_urls = [
            f'https://cars.usnews.com/images/{vehicle.brand.name.lower()}-{vehicle.model_name.lower()}-{image_number}.jpg',
            f'https://images.unsplash.com/photo-{image_number}?w=400&h=300',
        ]

        for image_url in image_urls:
            # 生成保存路径，使用英文文件名
            filename = f'{vehicle.brand.name}_{vehicle.model_name}_{vehicle.year}_{image_number}.jpg'.replace(' ', '_')
            save_path = Path(MEDIA_ROOT) / filename

            # 如果已经存在则跳过
            if save_path.exists():
                print(f'↻ 已存在: {filename}')
                continue

            # 尝试下载
            if download_image(image_url, save_path):
                # 创建VehiclePhoto记录
                vehicle.photos.create(
                    image=f'vehicles/{filename}',
                    is_main=(image_number == 1),
                    order=image_number
                )
                return True

        print(f'✗ 无法为{vehicle.brand.name} {vehicle.model_name} 下载图片')

    except Exception as e:
        print(f'✗ 处理错误: {str(e)}')

    return False

def fix_existing_images():
    """修复现有图片的文件名编码问题"""
    media_path = Path(MEDIA_ROOT)

    if not media_path.exists():
        print(f'✗ 媒体目录不存在: {media_path}')
        return

    # 遍历所有图片文件
    for old_file in media_path.glob('*'):
        if not old_file.is_file():
            continue

        # 检查是否有编码问题的文件名(含有中文或非标准格式)
        try:
            old_file.stat()  # 检查文件是否可访问
        except (UnicodeEncodeError, OSError):
            print(f'✗ 无法访问文件: {old_file.name}')
            continue

        # 如果扩展名格式不对(如_1jpg 应该是_1.jpg)
        if old_file.suffix.startswith('_') or not old_file.suffix:
            new_name = str(old_file.name).replace('_1jpg', '.jpg').replace('_2jpg', '.jpg').replace('_3jpg', '.jpg')
            new_path = old_file.parent / new_name

            try:
                old_file.rename(new_path)
                print(f'✓ 文件重命名: {old_file.name} → {new_name}')
            except Exception as e:
                print(f'✗ 重命名失败: {str(e)}')

def update_vehicle_photo_urls():
    """更新数据库中的图片URL"""
    try:
        vehicles = Vehicle.objects.all()

        for vehicle in vehicles:
            # 获取此车辆的所有图片
            photos = vehicle.photos.all()

            for photo in photos:
                # 检查图片路径是否需要修复
                if photo.image:
                    image_str = str(photo.image)

                    # 修复路径格式
                    if '_1jpg' in image_str or '_2jpg' in image_str or '_3jpg' in image_str:
                        image_str = image_str.replace('_1jpg', '.jpg').replace('_2jpg', '.jpg').replace('_3jpg', '.jpg')
                        photo.image = image_str
                        photo.save()
                        print(f'✓ 更新: {vehicle.brand.name} {vehicle.model_name} 的图片URL')

    except Exception as e:
        print(f'✗ 更新图片URL时出错: {str(e)}')

def main():
    """主函数"""
    print('=' * 60)
    print('车辆图片管理工具')
    print('=' * 60)

    # 修复现有图片
    print('\n[1] 修复现有图片...')
    fix_existing_images()

    # 更新数据库中的图片URL
    print('\n[2] 更新数据库中的图片URL...')
    update_vehicle_photo_urls()

    # 检查是否有车辆缺少图片
    print('\n[3] 检查缺少图片的车辆...')
    vehicles_without_photos = Vehicle.objects.filter(photos__isnull=True)

    if vehicles_without_photos.exists():
        print(f'找到 {vehicles_without_photos.count()} 个缺少图片的车辆')
        print('注意: 自动下载功能需要配置API密钥')
        print('建议: 手动上传高质量的车辆图片')
    else:
        print('✓ 所有车辆都有图片!')

    print('\n' + '=' * 60)
    print('完成!')
    print('=' * 60)

if __name__ == '__main__':
    main()
