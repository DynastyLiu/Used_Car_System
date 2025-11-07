"""
汽车品牌数据库
包含100+个真实汽车品牌及其相关信息
"""

CAR_BRANDS_DATA = [
    # 德国品牌
    {"name": "奥迪", "english_name": "Audi", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Audi-Logo_2016.svg/2560px-Audi-Logo_2016.svg.png"},
    {"name": "宝马", "english_name": "BMW", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/2560px-BMW.svg.png"},
    {"name": "奔驰", "english_name": "Mercedes-Benz", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Benz_logo_%282010%29.svg/2560px-Mercedes-Benz_logo_%282010%29.svg.png"},
    {"name": "大众", "english_name": "Volkswagen", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/2560px-Volkswagen_logo_2019.svg.png"},
    {"name": "保时捷", "english_name": "Porsche", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Porsche_logo.svg/2560px-Porsche_logo.svg.png"},
    {"name": "欧宝", "english_name": "Opel", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Opel_2017_logo.svg/2560px-Opel_2017_logo.svg.png"},

    # 日本品牌
    {"name": "丰田", "english_name": "Toyota", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Toyota_logo.svg/2560px-Toyota_logo.svg.png"},
    {"name": "本田", "english_name": "Honda", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Honda_Logo.svg/2560px-Honda_Logo.svg.png"},
    {"name": "日产", "english_name": "Nissan", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Nissan_2020_logo.svg/2560px-Nissan_2020_logo.svg.png"},
    {"name": "马自达", "english_name": "Mazda", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Mazda_logo.svg/2560px-Mazda_logo.svg.png"},
    {"name": "三菱", "english_name": "Mitsubishi", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Mitsubishi_Motors_logo.svg/2560px-Mitsubishi_Motors_logo.svg.png"},
    {"name": "斯巴鲁", "english_name": "Subaru", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Subaru_logo.svg/2560px-Subaru_logo.svg.png"},
    {"name": "铃木", "english_name": "Suzuki", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Suzuki_logo.svg/2560px-Suzuki_logo.svg.png"},
    {"name": "雷克萨斯", "english_name": "Lexus", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Lexus_logo.svg/2560px-Lexus_logo.svg.png"},
    {"name": "英菲尼迪", "english_name": "Infiniti", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Infiniti_logo.svg/2560px-Infiniti_logo.svg.png"},
    {"name": "讴歌", "english_name": "Acura", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Acura_logo.svg/2560px-Acura_logo.svg.png"},

    # 美国品牌
    {"name": "福特", "english_name": "Ford", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Ford_logo_flat.svg/2560px-Ford_logo_flat.svg.png"},
    {"name": "雪佛兰", "english_name": "Chevrolet", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Chevrolet_logo.svg/2560px-Chevrolet_logo.svg.png"},
    {"name": "凯迪拉克", "english_name": "Cadillac", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Cadillac_logo_2022.svg/2560px-Cadillac_logo_2022.svg.png"},
    {"name": "别克", "english_name": "Buick", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Buick_logo.svg/2560px-Buick_logo.svg.png"},
    {"name": "GMC", "english_name": "GMC", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/GMC_logo.svg/2560px-GMC_logo.svg.png"},
    {"name": "特斯拉", "english_name": "Tesla", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Tesla_Motors.svg/2560px-Tesla_Motors.svg.png"},
    {"name": "Jeep", "english_name": "Jeep", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Jeep_logo.svg/2560px-Jeep_logo.svg.png"},
    {"name": "道奇", "english_name": "Dodge", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Dodge_logo_2022.svg/2560px-Dodge_logo_2022.svg.png"},
    {"name": "克莱斯勒", "english_name": "Chrysler", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Chrysler_logo.svg/2560px-Chrysler_logo.svg.png"},
    {"name": "林肯", "english_name": "Lincoln", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Lincoln_Motor_Company_logo.svg/2560px-Lincoln_Motor_Company_logo.svg.png"},

    # 英国品牌
    {"name": "捷豹", "english_name": "Jaguar", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Jaguar_logo.svg/2560px-Jaguar_logo.svg.png"},
    {"name": "路虎", "english_name": "Land Rover", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Land_Rover_logo.svg/2560px-Land_Rover_logo.svg.png"},
    {"name": "宾利", "english_name": "Bentley", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Bentley_logo.svg/2560px-Bentley_logo.svg.png"},
    {"name": "劳斯莱斯", "english_name": "Rolls-Royce", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Rolls-Royce_logo.svg/2560px-Rolls-Royce_logo.svg.png"},
    {"name": "阿斯顿马丁", "english_name": "Aston Martin", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Aston_Martin_logo.svg/2560px-Aston_Martin_logo.svg.png"},
    {"name": "迷你", "english_name": "Mini", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Mini_logo.svg/2560px-Mini_logo.svg.png"},
    {"name": "迈凯伦", "english_name": "McLaren", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/McLaren_logo.svg/2560px-McLaren_logo.svg.png"},

    # 意大利品牌
    {"name": "法拉利", "english_name": "Ferrari", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Ferrari_logo.svg/2560px-Ferrari_logo.svg.png"},
    {"name": "兰博基尼", "english_name": "Lamborghini", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Lamborghini_logo.svg/2560px-Lamborghini_logo.svg.png"},
    {"name": "玛莎拉蒂", "english_name": "Maserati", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Maserati_logo.svg/2560px-Maserati_logo.svg.png"},
    {"name": "阿尔法罗密欧", "english_name": "Alfa Romeo", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Alfa_Romeo_logo.svg/2560px-Alfa_Romeo_logo.svg.png"},
    {"name": "菲亚特", "english_name": "Fiat", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Fiat_logo.svg/2560px-Fiat_logo.svg.png"},

    # 法国品牌
    {"name": "雷诺", "english_name": "Renault", "country": "法国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Renault_logo.svg/2560px-Renault_logo.svg.png"},
    {"name": "标致", "english_name": "Peugeot", "country": "法国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Peugeot_logo.svg/2560px-Peugeot_logo.svg.png"},
    {"name": "雪铁龙", "english_name": "Citroën", "country": "法国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Citro%C3%ABn_logo.svg/2560px-Citro%C3%ABn_logo.svg.png"},
    {"name": "布加迪", "english_name": "Bugatti", "country": "法国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Bugatti_logo.svg/2560px-Bugatti_logo.svg.png"},

    # 韩国品牌
    {"name": "现代", "english_name": "Hyundai", "country": "韩国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Hyundai_logo.svg/2560px-Hyundai_logo.svg.png"},
    {"name": "起亚", "english_name": "Kia", "country": "韩国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Kia_logo.svg/2560px-Kia_logo.svg.png"},
    {"name": "双龙", "english_name": "SsangYong", "country": "韩国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/SsangYong_logo.svg/2560px-SsangYong_logo.svg.png"},
    {"name": "捷恩斯", "english_name": "Genesis", "country": "韩国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Genesis_logo.svg/2560px-Genesis_logo.svg.png"},

    # 瑞典品牌
    {"name": "沃尔沃", "english_name": "Volvo", "country": "瑞典", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Volvo_logo.svg/2560px-Volvo_logo.svg.png"},
    {"name": "萨博", "english_name": "Saab", "country": "瑞典", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Saab_logo.svg/2560px-Saab_logo.svg.png"},
    {"name": "柯尼塞格", "english_name": "Koenigsegg", "country": "瑞典", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Koenigsegg_logo.svg/2560px-Koenigsegg_logo.svg.png"},

    # 中国品牌
    {"name": "比亚迪", "english_name": "BYD", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BYD_logo.svg/2560px-BYD_logo.svg.png"},
    {"name": "吉利", "english_name": "Geely", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Geely_logo.svg/2560px-Geely_logo.svg.png"},
    {"name": "长城", "english_name": "Great Wall", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Great_Wall_logo.svg/2560px-Great_Wall_logo.svg.png"},
    {"name": "奇瑞", "english_name": "Chery", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Chery_logo.svg/2560px-Chery_logo.svg.png"},
    {"name": "长安", "english_name": "Changan", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Changan_logo.svg/2560px-Changan_logo.svg.png"},
    {"name": "上汽荣威", "english_name": "Roewe", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Roewe_logo.svg/2560px-Roewe_logo.svg.png"},
    {"name": "上汽名爵", "english_name": "MG", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/MG_logo.svg/2560px-MG_logo.svg.png"},
    {"name": "东风风神", "english_name": "Dongfeng", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Dongfeng_logo.svg/2560px-Dongfeng_logo.svg.png"},
    {"name": "一汽奔腾", "english_name": "Bestune", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Bestune_logo.svg/2560px-Bestune_logo.svg.png"},
    {"name": "广汽传祺", "english_name": "GAC Trumpchi", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Trumpchi_logo.svg/2560px-Trumpchi_logo.svg.png"},
    {"name": "北汽绅宝", "english_name": "Senova", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Senova_logo.svg/2560px-Senova_logo.svg.png"},
    {"name": "江淮", "english_name": "JAC", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/JAC_logo.svg/2560px-JAC_logo.svg.png"},
    {"name": "中华", "english_name": "Brilliance", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Brilliance_logo.svg/2560px-Brilliance_logo.svg.png"},
    {"name": "海马", "english_name": "Haima", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Haima_logo.svg/2560px-Haima_logo.svg.png"},
    {"name": "力帆", "english_name": "Lifan", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Lifan_logo.svg/2560px-Lifan_logo.svg.png"},
    {"name": "众泰", "english_name": "Zotye", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Zotye_logo.svg/2560px-Zotye_logo.svg.png"},
    {"name": "蔚来", "english_name": "NIO", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/NIO_logo.svg/2560px-NIO_logo.svg.png"},
    {"name": "小鹏", "english_name": "XPeng", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/XPeng_logo.svg/2560px-XPeng_logo.svg.png"},
    {"name": "理想", "english_name": "Li Auto", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Li_Auto_logo.svg/2560px-Li_Auto_logo.svg.png"},
    {"name": "威马", "english_name": "WM Motor", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/WM_Motor_logo.svg/2560px-WM_Motor_logo.svg.png"},
    {"name": "零跑", "english_name": "Leapmotor", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Leapmotor_logo.svg/2560px-Leapmotor_logo.svg.png"},

    # 更多豪华品牌
    {"name": "迈巴赫", "english_name": "Maybach", "country": "德国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Maybach_logo.svg/2560px-Maybach_logo.svg.png"},
    {"name": "世爵", "english_name": "Spyker", "country": "荷兰", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Spyker_logo.svg/2560px-Spyker_logo.svg.png"},
    {"name": "帕加尼", "english_name": "Pagani", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Pagani_logo.svg/2560px-Pagani_logo.svg.png"},
    {"name": "西雅特", "english_name": "SEAT", "country": "西班牙", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/SEAT_logo.svg/2560px-SEAT_logo.svg.png"},
    {"name": "达契亚", "english_name": "Dacia", "country": "罗马尼亚", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Dacia_logo.svg/2560px-Dacia_logo.svg.png"},
    {"name": "斯柯达", "english_name": "Škoda", "country": "捷克", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/%C5%A0koda_logo.svg/2560px-%C5%A0koda_logo.svg.png"},
    {"name": "霍顿", "english_name": "Holden", "country": "澳大利亚", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Holden_logo.svg/2560px-Holden_logo.svg.png"},

    # 更多新兴品牌
    {"name": "Rivian", "english_name": "Rivian", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Rivian_logo.svg/2560px-Rivian_logo.svg.png"},
    {"name": "Lucid", "english_name": "Lucid Motors", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Lucid_Motors_logo.svg/2560px-Lucid_Motors_logo.svg.png"},
    {"name": "极星", "english_name": "Polestar", "country": "瑞典", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Polestar_logo.svg/2560px-Polestar_logo.svg.png"},
    {"name": "爱驰", "english_name": "Aiways", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Aiways_logo.svg/2560px-Aiways_logo.svg.png"},
    {"name": "天际", "english_name": "ENOVATE", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/ENOVATE_logo.svg/2560px-ENOVATE_logo.svg.png"},

    # 更多经典品牌
    {"name": "罗孚", "english_name": "Rover", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Rover_logo.svg/2560px-Rover_logo.svg.png"},
    {"name": "TVR", "english_name": "TVR", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/TVR_logo.svg/2560px-TVR_logo.svg.png"},
    {"name": "莲花", "english_name": "Lotus", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Lotus_logo.svg/2560px-Lotus_logo.svg.png"},
    {"name": "摩根", "english_name": "Morgan", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Morgan_logo.svg/2560px-Morgan_logo.svg.png"},

    # 更多实用品牌
    {"name": "五十铃", "english_name": "Isuzu", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Isuzu_logo.svg/2560px-Isuzu_logo.svg.png"},
    {"name": "日野", "english_name": "Hino", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Hino_logo.svg/2560px-Hino_logo.svg.png"},
    {"name": "UD卡车", "english_name": "UD Trucks", "country": "日本", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/UD_Trucks_logo.svg/2560px-UD_Trucks_logo.svg.png"},

    # 更多新兴电动品牌
    {"name": "Rimac", "english_name": "Rimac", "country": "克罗地亚", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Rimac_logo.svg/2560px-Rimac_logo.svg.png"},
    {"name": "Pininfarina", "english_name": "Pininfarina", "country": "意大利", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Pininfarina_logo.svg/2560px-Pininfarina_logo.svg.png"},
    {"name": "Fisker", "english_name": "Fisker", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Fisker_logo.svg/2560px-Fisker_logo.svg.png"},
    {"name": "Canoo", "english_name": "Canoo", "country": "美国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Canoo_logo.svg/2560px-Canoo_logo.svg.png"},
    {"name": "Arrival", "english_name": "Arrival", "country": "英国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Arrival_logo.svg/2560px-Arrival_logo.svg.png"},

    # 更多中国品牌
    {"name": "红旗", "english_name": "Hongqi", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Hongqi_logo.svg/2560px-Hongqi_logo.svg.png"},
    {"name": "东风风行", "english_name": "Fengxing", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Fengxing_logo.svg/2560px-Fengxing_logo.svg.png"},
    {"name": "一汽骏派", "english_name": "Junpai", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Junpai_logo.svg/2560px-Junpai_logo.svg.png"},
    {"name": "开瑞", "english_name": "Karry", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Karry_logo.svg/2560px-Karry_logo.svg.png"},
    {"name": "猎豹", "english_name": "Leopaard", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Leopaard_logo.svg/2560px-Leopaard_logo.svg.png"},
    {"name": "陆风", "english_name": "Landwind", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Landwind_logo.svg/2560px-Landwind_logo.svg.png"},
    {"name": "华泰", "english_name": "Hawtai", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Hawtai_logo.svg/2560px-Hawtai_logo.svg.png"},
    {"name": "昌河", "english_name": "Changhe", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Changhe_logo.svg/2560px-Changhe_logo.svg.png"},
    {"name": "福田", "english_name": "Foton", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Foton_logo.svg/2560px-Foton_logo.svg.png"},
    {"name": "黄海", "english_name": "Huanghai", "country": "中国", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Huanghai_logo.svg/2560px-Huanghai_logo.svg.png"},

    # 更多国际品牌
    {"name": "塔塔", "english_name": "Tata", "country": "印度", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Tata_logo.svg/2560px-Tata_logo.svg.png"},
    {"name": "马恒达", "english_name": "Mahindra", "country": "印度", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Mahindra_logo.svg/2560px-Mahindra_logo.svg.png"},
    {"name": "拉达", "english_name": "Lada", "country": "俄罗斯", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Lada_logo.svg/2560px-Lada_logo.svg.png"},
    {"name": "GAZ", "english_name": "GAZ", "country": "俄罗斯", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/GAZ_logo.svg/2560px-GAZ_logo.svg.png"},
    {"name": "UAZ", "english_name": "UAZ", "country": "俄罗斯", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/UAZ_logo.svg/2560px-UAZ_logo.svg.png"},
    {"name": "Proton", "english_name": "Proton", "country": "马来西亚", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Proton_logo.svg/2560px-Proton_logo.svg.png"},
    {"name": "Perodua", "english_name": "Perodua", "country": "马来西亚", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Perodua_logo.svg/2560px-Perodua_logo.svg.png"},
]

def get_all_brands():
    """获取所有汽车品牌数据"""
    return CAR_BRANDS_DATA

def get_brands_by_country(country):
    """根据国家获取品牌"""
    return [brand for brand in CAR_BRANDS_DATA if brand['country'] == country]

def search_brands(keyword):
    """搜索品牌"""
    keyword = keyword.lower()
    return [brand for brand in CAR_BRANDS_DATA
            if keyword in brand['name'].lower() or
               keyword in brand['english_name'].lower()]