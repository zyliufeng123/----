"""
自动物品导入器
- 从OCR识别结果自动导入物品
- 智能提取价格、稀有度等信息
- 完全自动化，无需手动填写
"""

import json
import re
from pathlib import Path
from datetime import datetime

class AutoItemImporter:
    """
    自动物品导入器
    """
    
    def __init__(self):
        self.items_db_file = "data/items/items_database.json"
        self.unknown_items_file = "data/unknown_items.json"
        self.price_history_file = "data/price_history.json"
        
        # 加载现有数据
        self.items_db = self.load_items_database()
        self.price_data = self.load_price_data()
        
    def load_items_database(self):
        """加载物品数据库"""
        if Path(self.items_db_file).exists():
            with open(self.items_db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {item['name']: item for item in data.get('items', [])}
        return {}
    
    def load_price_data(self):
        """加载价格数据"""
        if Path(self.price_history_file).exists():
            with open(self.price_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def auto_import_unknown_items(self):
        """
        自动导入未知物品
        
        策略：
        1. 从价格历史中获取价格
        2. 根据物品名称自动判断类型
        3. 根据价格区间自动判断稀有度
        4. 批量导入到数据库
        """
        
        if not Path(self.unknown_items_file).exists():
            print("❌ 未找到未知物品文件")
            return
        
        # 读取未知物品
        with open(self.unknown_items_file, 'r', encoding='utf-8') as f:
            unknown_items = json.load(f)
        
        print("="*60)
        print("🔄 开始自动导入未知物品")
        print("="*60)
        
        imported_count = 0
        skipped_count = 0
        
        for item in unknown_items:
            item_name = item['name']
            
            # 跳过已存在的物品
            if item_name in self.items_db:
                print(f"⏭️  跳过已存在: {item_name}")
                skipped_count += 1
                continue
            
            # 跳过不是物品的文本（如：通用关键词）
            if not self.is_valid_item(item_name):
                print(f"⚠️  无效物品: {item_name}")
                skipped_count += 1
                continue
            
            # 尝试从价格数据中获取信息
            price_info = self.price_data.get(item_name, None)
            
            if price_info:
                # 有价格数据，使用实际价格
                avg_price = self.calculate_avg_price(price_info)
                rarity = self.determine_rarity_by_price(avg_price)
                
                print(f"✅ 导入: {item_name:<30} {avg_price:>8,} 币 [{rarity}]")
            else:
                # 无价格数据，使用默认估值
                estimated_price = self.estimate_price(item_name)
                rarity = self.determine_rarity_by_price(estimated_price)
                
                print(f"🔸 导入(估值): {item_name:<30} {estimated_price:>8,} 币 [{rarity}]")
            
            # 添加到数据库
            new_item = {
                'name': item_name,
                'value': price_info['prices'][-1]['price'] if price_info else estimated_price,
                'avg_value': avg_price if price_info else estimated_price,
                'rarity': rarity,
                'category': self.determine_category(item_name),
                'auto_imported': True,
                'import_time': datetime.now().isoformat(),
                'confidence': item.get('confidence', 0.8)
            }
            
            self.items_db[item_name] = new_item
            imported_count += 1
        
        # 保存到文件
        if imported_count > 0:
            self.save_items_database()
            print(f"\n💾 已保存 {imported_count} 个新物品到数据库")
        
        print("\n" + "="*60)
        print("📊 导入统计")
        print("="*60)
        print(f"成功导入：{imported_count}")
        print(f"跳过物品：{skipped_count}")
        print("="*60)
        
        # 清空未知物品列表（可选）
        self.clear_unknown_items()
    
    def is_valid_item(self, name):
        """
        验证是否是有效的物品名称
        排除：通用关键词、界面元素等
        """
        # 排除通用关键词
        invalid_keywords = [
            '装备', '武器', '头盔', '护甲', '背包',  # 太泛的
            '交易行', '仓库', '特勤处', '开始游戏',  # 界面元素
            'FIRST', 'AID', 'HELP', 'EXIT',  # 英文界面词
            '确定', '取消', '返回', '关闭'  # 按钮文字
        ]
        
        # 完全匹配这些词的，跳过
        if name in invalid_keywords:
            return False
        
        # 太短的跳过
        if len(name) < 3:
            return False
        
        # 全是数字的跳过
        if name.isdigit():
            return False
        
        return True
    
    def calculate_avg_price(self, price_info):
        """计算平均价格"""
        prices = [p['price'] for p in price_info.get('prices', [])]
        return int(sum(prices) / len(prices)) if prices else 0
    
    def estimate_price(self, item_name):
        """
        根据物品名称估算价格
        
        策略：
        - 特定品牌/型号的武器：高价值
        - 稀有/精英关键词：中高价值
        - 训练/基础关键词：低价值
        """
        
        # 高价值关键词
        high_value_keywords = [
            '精英', '稀有', '传说', '史诗', '黄金', '特种',
            'KC17', 'K416', 'M7', 'HK', 'SCAR-H'
        ]
        
        # 中价值关键词
        mid_value_keywords = [
            '战术', '重型', '夜视', '防暴', '突击',
            'M4A1', 'AK', 'AUG', 'AS Val'
        ]
        
        # 低价值关键词
        low_value_keywords = [
            '训练', '基础', '标准', '轻型',
            'QBZ', 'SG552', 'G3', 'CAR-15'
        ]
        
        # 判断价值等级
        for keyword in high_value_keywords:
            if keyword in item_name:
                return 150000  # 高价
        
        for keyword in mid_value_keywords:
            if keyword in item_name:
                return 80000  # 中价
        
        for keyword in low_value_keywords:
            if keyword in item_name:
                return 30000  # 低价
        
        # 默认中等价格
        return 50000
    
    def determine_rarity_by_price(self, price):
        """根据价格判断稀有度"""
        if price >= 150000:
            return 'epic'
        elif price >= 80000:
            return 'rare'
        elif price >= 40000:
            return 'uncommon'
        else:
            return 'common'
    
    def determine_category(self, item_name):
        """根据名称判断物品类别"""
        
        weapon_keywords = [
            '步枪', '突击', '战斗', '狙击', '手枪', '霰弹', '冲锋',
            '机枪', '榴弹', '火箭'
        ]
        
        armor_keywords = ['头盔', '护甲', '背心', '防弹']
        
        equipment_keywords = ['背包', '腰带', '手套', '靴子', '护目镜']
        
        material_keywords = ['砖', '板', '金属', '芯片', '零件', '电路']
        
        for kw in weapon_keywords:
            if kw in item_name:
                return 'weapon'
        
        for kw in armor_keywords:
            if kw in item_name:
                return 'armor'
        
        for kw in equipment_keywords:
            if kw in item_name:
                return 'equipment'
        
        for kw in material_keywords:
            if kw in item_name:
                return 'material'
        
        return 'unknown'
    
    def save_items_database(self):
        """保存物品数据库"""
        Path(self.items_db_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为列表格式
        items_list = list(self.items_db.values())
        
        data = {
            'version': '1.0',
            'last_update': datetime.now().isoformat(),
            'items': items_list
        }
        
        with open(self.items_db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def clear_unknown_items(self):
        """清空未知物品列表（可选）"""
        with open(self.unknown_items_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        print("🗑️  已清空未知物品列表")


def main():
    """主函数"""
    print("="*60)
    print("🤖 自动物品导入器")
    print("="*60)
    print()
    
    importer = AutoItemImporter()
    
    print("📋 开始自动导入...")
    importer.auto_import_unknown_items()
    
    print("\n✅ 导入完成！")
    print("\n💡 下次运行识别工具时，这些物品将自动被识别")


if __name__ == "__main__":
    main()