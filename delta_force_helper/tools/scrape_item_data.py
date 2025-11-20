"""
三角洲行动物品数据爬虫
从 zxfps.com 获取物品信息
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin
import re

class ItemDataScraper:
    def __init__(self):
        self.base_url = "https://www.zxfps.com"
        self.tool_url = "https://tool.zxfps.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.item_database = {
            'weapons': [],
            'equipment': [],
            'consumables': [],
            'valuables': [],
            'ammo': []
        }
    
    def scrape_all(self):
        """爬取所有物品数据"""
        print("="*60)
        print("🕷️  三角洲行动物品数据爬虫")
        print("="*60)
        print(f"\n目标网站：{self.tool_url}")
        print("开始爬取...\n")
        
        try:
            # 先尝试获取主页
            print("📡 正在连接网站...")
            response = self.session.get(self.tool_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 网站连接成功\n")
                
                # 尝试解析页面结构
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找物品数据的API或数据结构
                # 这里需要分析网站的实际结构
                self.analyze_page_structure(soup)
                
            else:
                print(f"❌ 网站访问失败：HTTP {response.status_code}")
                print("使用备用方案：手动配置数据...")
                self.use_fallback_data()
        
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
            print("\n使用备用方案：预设常见物品数据...")
            self.use_fallback_data()
    
    def analyze_page_structure(self, soup):
        """分析网页结构"""
        print("🔍 正在分析网页结构...")
        
        # 查找可能的数据容器
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and 'item' in script.string.lower():
                print(f"📄 找到可能包含物品数据的脚本")
                # 尝试提取JSON数据
                self.extract_json_from_script(script.string)
        
        # 查找表格或列表
        tables = soup.find_all('table')
        if tables:
            print(f"📊 找到 {len(tables)} 个表格")
        
        divs = soup.find_all('div', class_=re.compile(r'item|weapon|loot'))
        if divs:
            print(f"📦 找到 {len(divs)} 个物品容器")
    
    def extract_json_from_script(self, script_text):
        """从脚本中提取JSON数据"""
        try:
            # 尝试找到JSON数据
            json_pattern = r'\{.*?\}'
            matches = re.findall(json_pattern, script_text, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if 'name' in data or 'price' in data:
                        print(f"✅ 提取到物品数据：{data}")
                except:
                    continue
        except Exception as e:
            print(f"⚠️  JSON提取失败：{e}")
    
    def use_fallback_data(self):
        """使用预设的常见物品数据"""
        print("\n" + "="*60)
        print("📚 使用预设物品数据库")
        print("="*60)
        
        # 武器类
        self.item_database['weapons'] = [
            {
                'id': 'weapon_001',
                'name': 'M4A1',
                'name_cn': 'M4A1突击步枪',
                'category': 'weapons',
                'subcategory': '突击步枪',
                'price': 4000,
                'rarity': 'common',
                'description': '5.56mm突击步枪，通用性强'
            },
            {
                'id': 'weapon_002',
                'name': 'AK-47',
                'name_cn': 'AK-47突击步枪',
                'category': 'weapons',
                'subcategory': '突击步枪',
                'price': 3800,
                'rarity': 'common',
                'description': '7.62mm突击步枪，威力大'
            },
            {
                'id': 'weapon_003',
                'name': 'AWM',
                'name_cn': 'AWM狙击步枪',
                'category': 'weapons',
                'subcategory': '狙击步枪',
                'price': 8500,
                'rarity': 'rare',
                'description': '高精度狙击步枪'
            },
            {
                'id': 'weapon_004',
                'name': 'MP5',
                'name_cn': 'MP5冲锋枪',
                'category': 'weapons',
                'subcategory': '冲锋枪',
                'price': 2800,
                'rarity': 'common',
                'description': '近距离战斗武器'
            },
            {
                'id': 'weapon_005',
                'name': 'M870',
                'name_cn': 'M870霰弹枪',
                'category': 'weapons',
                'subcategory': '霰弹枪',
                'price': 3200,
                'rarity': 'common',
                'description': '近距离散弹武器'
            }
        ]
        
        # 装备类
        self.item_database['equipment'] = [
            {
                'id': 'equip_001',
                'name': 'Helmet_Lv1',
                'name_cn': '一级头盔',
                'category': 'equipment',
                'subcategory': '头盔',
                'price': 800,
                'rarity': 'common',
                'description': '基础防护头盔'
            },
            {
                'id': 'equip_002',
                'name': 'Helmet_Lv2',
                'name_cn': '二级头盔',
                'category': 'equipment',
                'subcategory': '头盔',
                'price': 1500,
                'rarity': 'uncommon',
                'description': '中级防护头盔'
            },
            {
                'id': 'equip_003',
                'name': 'Helmet_Lv3',
                'name_cn': '三级头盔',
                'category': 'equipment',
                'subcategory': '头盔',
                'price': 2800,
                'rarity': 'rare',
                'description': '高级防护头盔'
            },
            {
                'id': 'equip_004',
                'name': 'Vest_Lv1',
                'name_cn': '一级护甲',
                'category': 'equipment',
                'subcategory': '护甲',
                'price': 1000,
                'rarity': 'common',
                'description': '基础防护背心'
            },
            {
                'id': 'equip_005',
                'name': 'Vest_Lv2',
                'name_cn': '二级护甲',
                'category': 'equipment',
                'subcategory': '护甲',
                'price': 1800,
                'rarity': 'uncommon',
                'description': '中级防护背心'
            },
            {
                'id': 'equip_006',
                'name': 'Vest_Lv3',
                'name_cn': '三级护甲',
                'category': 'equipment',
                'subcategory': '护甲',
                'price': 3500,
                'rarity': 'rare',
                'description': '高级防护背心'
            },
            {
                'id': 'equip_007',
                'name': 'Backpack_Small',
                'name_cn': '小型背包',
                'category': 'equipment',
                'subcategory': '背包',
                'price': 500,
                'rarity': 'common',
                'description': '增加携带容量'
            },
            {
                'id': 'equip_008',
                'name': 'Backpack_Large',
                'name_cn': '大型背包',
                'category': 'equipment',
                'subcategory': '背包',
                'price': 1200,
                'rarity': 'uncommon',
                'description': '大幅增加携带容量'
            }
        ]
        
        # 消耗品类
        self.item_database['consumables'] = [
            {
                'id': 'consume_001',
                'name': 'Medkit',
                'name_cn': '医疗包',
                'category': 'consumables',
                'subcategory': '医疗',
                'price': 300,
                'rarity': 'common',
                'description': '恢复生命值'
            },
            {
                'id': 'consume_002',
                'name': 'FirstAid',
                'name_cn': '急救包',
                'category': 'consumables',
                'subcategory': '医疗',
                'price': 150,
                'rarity': 'common',
                'description': '快速恢复少量生命'
            },
            {
                'id': 'consume_003',
                'name': 'Bandage',
                'name_cn': '绷带',
                'category': 'consumables',
                'subcategory': '医疗',
                'price': 50,
                'rarity': 'common',
                'description': '缓慢恢复生命'
            },
            {
                'id': 'consume_004',
                'name': 'Painkiller',
                'name_cn': '止痛药',
                'category': 'consumables',
                'subcategory': '医疗',
                'price': 100,
                'rarity': 'common',
                'description': '提升移动速度'
            },
            {
                'id': 'consume_005',
                'name': 'EnergyDrink',
                'name_cn': '能量饮料',
                'category': 'consumables',
                'subcategory': '增益',
                'price': 80,
                'rarity': 'common',
                'description': '短暂提升性能'
            }
        ]
        
        # 弹药类
        self.item_database['ammo'] = [
            {
                'id': 'ammo_001',
                'name': 'Ammo_556',
                'name_cn': '5.56mm弹药',
                'category': 'ammo',
                'subcategory': '步枪弹',
                'price': 250,
                'unit_price': 4.17,  # 每60发
                'stack_size': 60,
                'rarity': 'common',
                'description': '5.56mm步枪弹药'
            },
            {
                'id': 'ammo_002',
                'name': 'Ammo_762',
                'name_cn': '7.62mm弹药',
                'category': 'ammo',
                'subcategory': '步枪弹',
                'price': 280,
                'unit_price': 4.67,
                'stack_size': 60,
                'rarity': 'common',
                'description': '7.62mm步枪弹药'
            },
            {
                'id': 'ammo_003',
                'name': 'Ammo_9mm',
                'name_cn': '9mm弹药',
                'category': 'ammo',
                'subcategory': '手枪弹',
                'price': 150,
                'unit_price': 3.00,
                'stack_size': 50,
                'rarity': 'common',
                'description': '9mm手枪弹药'
            },
            {
                'id': 'ammo_004',
                'name': 'Ammo_12gauge',
                'name_cn': '12号霰弹',
                'category': 'ammo',
                'subcategory': '霰弹',
                'price': 200,
                'unit_price': 6.67,
                'stack_size': 30,
                'rarity': 'common',
                'description': '12号霰弹枪弹药'
            }
        ]
        
        # 贵重品类
        self.item_database['valuables'] = [
            {
                'id': 'valuable_001',
                'name': 'Mandelbrick',
                'name_cn': '曼德尔砖',
                'category': 'valuables',
                'subcategory': '高价值物品',
                'price': 9800,
                'rarity': 'epic',
                'description': '极高价值的贵重物品',
                'weight': 2.0
            },
            {
                'id': 'valuable_002',
                'name': 'Intelligence',
                'name_cn': '情报文件',
                'category': 'valuables',
                'subcategory': '高价值物品',
                'price': 7500,
                'rarity': 'rare',
                'description': '重要情报资料',
                'weight': 0.5
            },
            {
                'id': 'valuable_003',
                'name': 'GoldBar',
                'name_cn': '金条',
                'category': 'valuables',
                'subcategory': '高价值物品',
                'price': 5000,
                'rarity': 'rare',
                'description': '纯金金条',
                'weight': 1.0
            },
            {
                'id': 'valuable_004',
                'name': 'Jewelry',
                'name_cn': '珠宝',
                'category': 'valuables',
                'subcategory': '中等价值物品',
                'price': 2500,
                'rarity': 'uncommon',
                'description': '贵重珠宝',
                'weight': 0.3
            },
            {
                'id': 'valuable_005',
                'name': 'Watch',
                'name_cn': '名表',
                'category': 'valuables',
                'subcategory': '中等价值物品',
                'price': 1800,
                'rarity': 'uncommon',
                'description': '高档手表',
                'weight': 0.2
            }
        ]
        
        print(f"\n✅ 数据库构建完成：")
        print(f"   - 武器：{len(self.item_database['weapons'])} 种")
        print(f"   - 装备：{len(self.item_database['equipment'])} 种")
        print(f"   - 消耗品：{len(self.item_database['consumables'])} 种")
        print(f"   - 弹药：{len(self.item_database['ammo'])} 种")
        print(f"   - 贵重品：{len(self.item_database['valuables'])} 种")
        
        total_items = sum(len(v) for v in self.item_database.values())
        print(f"   总计：{total_items} 种物品")
    
    def save_database(self, output_path='data/item_database.json'):
        """保存物品数据库"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.item_database, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存：{output_path}")
    
    def download_icons(self):
        """下载物品图标（如果网站提供）"""
        print("\n" + "="*60)
        print("📥 图标下载")
        print("="*60)
        
        # 由于网站结构未知，暂时跳过
        print("⚠️  图标需要手动采集或使用占位符")
        print("💡 方案：游戏内实际截图提取")
        
        # 创建占位符
        self.create_icon_placeholders()
    
    def create_icon_placeholders(self):
        """创建图标占位符信息"""
        icon_info = {
            'status': 'placeholder',
            'note': '需要从游戏内实际截图提取物品图标',
            'required_icons': []
        }
        
        for category, items in self.item_database.items():
            for item in items:
                icon_info['required_icons'].append({
                    'item_id': item['id'],
                    'item_name': item['name_cn'],
                    'icon_path': f"recognition/models/templates/{item['id']}.png",
                    'status': 'missing'
                })
        
        with open('data/icon_status.json', 'w', encoding='utf-8') as f:
            json.dump(icon_info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 图标信息已生成：data/icon_status.json")

def main():
    scraper = ItemDataScraper()
    
    # 爬取数据
    scraper.scrape_all()
    
    # 保存数据库
    scraper.save_database()
    
    # 处理图标
    scraper.download_icons()
    
    print("\n" + "="*60)
    print("🎉 第一步完成！")
    print("="*60)
    print("\n📋 下一步：")
    print("   1. 查看生成的物品数据库：data/item_database.json")
    print("   2. 准备从游戏内截取物品图标")
    print("   3. 开发识别算法\n")

if __name__ == "__main__":
    main()