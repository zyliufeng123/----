"""
智能导入器 - 从价格追踪数据自动生成物品数据库
"""

import json
from pathlib import Path
from datetime import datetime

class SmartImporter:
    """
    智能导入器
    
    特点：
    - 完全依赖价格追踪数据
    - 有多少条价格记录就导入多少物品
    - 价格、稀有度全自动
    """
    
    def __init__(self):
        self.price_history_file = "data/price_history.json"
        self.items_db_file = "data/items/items_database.json"
        self.current_prices_file = "data/current_prices.json"
    
    def import_from_price_data(self):
        """
        从价格数据自动生成物品数据库
        """
        
        # 检查价格数据
        if not Path(self.price_history_file).exists():
            print("❌ 未找到价格数据，请先运行价格采集")
            print("   python tools\\price_tracker.py")
            return
        
        # 加载价格数据
        with open(self.price_history_file, 'r', encoding='utf-8') as f:
            price_history = json.load(f)
        
        if not price_history:
            print("❌ 价格数据为空")
            return
        
        print("="*60)
        print("🤖 智能导入 - 从价格数据生成物品库")
        print("="*60)
        print(f"📊 发现 {len(price_history)} 个物品的价格数据")
        print()
        
        # 生成物品列表
        items = []
        
        for name, data in price_history.items():
            prices = [p['price'] for p in data.get('prices', [])]
            
            if not prices:
                continue
            
            # 计算统计数据
            avg_price = int(sum(prices) / len(prices))
            min_price = min(prices)
            max_price = max(prices)
            latest_price = prices[-1]
            
            # 自动判断稀有度
            rarity = self.auto_detect_rarity(avg_price)
            
            # 自动判断类别
            category = self.auto_detect_category(name)
            
            item = {
                'name': name,
                'value': latest_price,
                'avg_value': avg_price,
                'min_value': min_price,
                'max_value': max_price,
                'rarity': rarity,
                'category': category,
                'price_samples': len(prices),
                'auto_generated': True,
                'last_update': data.get('last_update', datetime.now().isoformat())
            }
            
            items.append(item)
            
            # 显示导入信息
            print(f"✅ {name:<30} {avg_price:>8,} 币 [{rarity}] ({len(prices)}次采样)")
        
        # 保存到数据库
        if items:
            self.save_database(items)
            
            print("\n" + "="*60)
            print("💾 导入完成")
            print("="*60)
            print(f"导入物品数：{len(items)}")
            print(f"保存位置：{self.items_db_file}")
            print("="*60)
        else:
            print("\n❌ 没有可导入的物品")
    
    def auto_detect_rarity(self, avg_price):
        """根据平均价格自动判断稀有度"""
        if avg_price >= 180000:
            return 'epic'
        elif avg_price >= 100000:
            return 'rare'
        elif avg_price >= 50000:
            return 'uncommon'
        else:
            return 'common'
    
    def auto_detect_category(self, name):
        """自动检测物品类别"""
        categories = {
            'weapon': ['步枪', '突击', '战斗', '狙击', '手枪', '霰弹', '冲锋', '机枪'],
            'armor': ['头盔', '护甲', '背心', '防弹'],
            'equipment': ['背包', '腰带', '手套', '靴子', '护目镜', '战术'],
            'material': ['砖', '板', '金属', '芯片', '零件', '电路', '材料']
        }
        
        for category, keywords in categories.items():
            if any(kw in name for kw in keywords):
                return category
        
        return 'unknown'
    
    def save_database(self, items):
        """保存数据库"""
        Path(self.items_db_file).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'version': '1.0',
            'last_update': datetime.now().isoformat(),
            'auto_generated': True,
            'items': items
        }
        
        with open(self.items_db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print("="*60)
    print("🤖 智能物品导入器")
    print("="*60)
    print()
    
    importer = SmartImporter()
    importer.import_from_price_data()
    
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()