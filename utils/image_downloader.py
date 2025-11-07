"""
图片下载管理器
用于下载和存储车标和车辆图片
"""

import os
import requests
from PIL import Image
import io
from django.conf import settings
from pathlib import Path

class ImageDownloader:
    def __init__(self):
        self.base_path = Path(settings.MEDIA_ROOT) / 'brand_logos'
        self.base_path.mkdir(parents=True, exist_ok=True)

    def download_image(self, url, filename, max_size=(256, 256)):
        """
        下载并保存图片

        Args:
            url (str): 图片URL
            filename (str): 保存的文件名
            max_size (tuple): 最大尺寸(width, height)

        Returns:
            str: 保存的文件路径
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # 使用PIL处理图片
            image = Image.open(io.BytesIO(response.content))

            # 转换为RGB模式（处理RGBA等格式）
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # 调整图片大小
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 保存文件
            file_path = self.base_path / filename
            image.save(file_path, 'JPEG', quality=90, optimize=True)

            return f'brand_logos/{filename}'

        except requests.exceptions.RequestException as e:
            print(f"下载图片失败 {url}: {e}")
            return None
        except Exception as e:
            print(f"处理图片失败 {url}: {e}")
            return None

    def download_brand_logo(self, brand_name, logo_url, force_download=False):
        """
        下载品牌车标

        Args:
            brand_name (str): 品牌名称
            logo_url (str): 车标URL
            force_download (bool): 是否强制重新下载

        Returns:
            str: 保存的文件路径
        """
        # 清理品牌名称，用作文件名
        safe_name = "".join(c for c in brand_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}.jpg"

        # 检查文件是否已存在
        file_path = self.base_path / filename
        if not force_download and file_path.exists():
            return f"brand_logos/{filename}"

        return self.download_image(logo_url, filename)

    def download_vehicle_image(self, vehicle_name, image_url):
        """
        下载车辆图片

        Args:
            vehicle_name (str): 车辆名称
            image_url (str): 图片URL

        Returns:
            str: 保存的文件路径
        """
        # 清理车辆名称，用作文件名
        safe_name = "".join(c for c in vehicle_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}.jpg"

        return self.download_image(image_url, filename, max_size=(800, 600))

def get_placeholder_logo_url(brand_name):
    """
    获取占位符车标URL

    Args:
        brand_name (str): 品牌名称

    Returns:
        str: 占位符图片URL
    """
    # 使用在线占位符服务
    return f"https://via.placeholder.com/256x256/4A90E2/FFFFFF?text={brand_name}"

def get_placeholder_vehicle_url(vehicle_name):
    """
    获取占位符车辆图片URL

    Args:
        vehicle_name (str): 车辆名称

    Returns:
        str: 占位符图片URL
    """
    # 使用在线占位符服务
    return f"https://via.placeholder.com/800x600/4A90E2/FFFFFF?text={vehicle_name}"