"""
导入汽车品牌管理命令
"""

from django.core.management.base import BaseCommand
from vehicles.models import CarBrand
from utils.car_brands_data import get_all_brands
from utils.image_downloader import ImageDownloader
import time

class Command(BaseCommand):
    help = '导入汽车品牌数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--download-logos',
            action='store_true',
            help='下载品牌车标图片',
        )
        parser.add_argument(
            '--force-download',
            action='store_true',
            help='强制重新下载所有品牌车标图片',
        )

    def handle(self, *args, **options):
        self.stdout.write('开始导入汽车品牌数据..')

        downloader = ImageDownloader()
        brands_data = get_all_brands()

        imported_count = 0
        skipped_count = 0

        for brand_data in brands_data:
            try:
                brand = None
                # 检查品牌是否已存在
                if CarBrand.objects.filter(name=brand_data['name']).exists():
                    if not options['force_download'] and not options['download_logos']:
                        self.stdout.write(f"品牌 '{brand_data['name']}' 已存在，跳过")
                        skipped_count += 1
                        continue
                    brand = CarBrand.objects.get(name=brand_data['name'])
                else:
                    # 创建品牌记录
                    brand = CarBrand.objects.create(
                        name=brand_data['name'],
                        country=brand_data['country'],
                        description=f"{brand_data['english_name']} - {brand_data['country']}品牌",
                        is_active=True
                    )
                    imported_count += 1

                # 下载车标
                if (options['download_logos'] or options['force_download']) and brand_data['logo_url']:
                    self.stdout.write(f"正在下载 {brand_data['name']} 的车标..")
                    logo_path = downloader.download_brand_logo(
                        brand_data['name'],
                        brand_data['logo_url'],
                        force_download=options['force_download']
                    )
                    if logo_path:
                        # 更新车标路径
                        brand.logo = logo_path
                        brand.save()
                        self.stdout.write(f"车标下载成功: {logo_path}")
                    else:
                        self.stdout.write(self.style.WARNING(f"车标下载失败: {brand_data['name']}"))
                    time.sleep(1)  # 避免请求过快

                if not options['force_download'] and not options['download_logos']:
                    self.stdout.write(f"成功导入品牌: {brand.name}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"处理品牌失败 {brand_data['name']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(
            f"导入完成！成功导入 {imported_count} 个品牌，跳过 {skipped_count} 个已存在的品牌"
        ))