"""
游戏截图自动分析工具（带自动学习）
"""

import cv2
import numpy as np
from pathlib import Path
import json
import easyocr
from PIL import Image
import re

class ScreenshotAnalyzer:
    """
    游戏截图分析器（支持未知物品记录）
    """
    
    def __init__(self, database_path="data/items/items_database.json"):
        print("🔧 初始化识别引擎...")
        
        print("   加载OCR引擎...")
        self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        
        print("   加载物品数据库...")
        self.load_database(database_path)
        
        # 【新增】未知物品记录
        self.unknown_items = []
        self.unknown_items_file = "data/unknown_items.json"
        
        print("✅ 初始化完成！\n")
    
    def load_database(self, db_path):
        """加载物品价格数据库"""
        if Path(db_path).exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.items_db = {item['name']: item for item in data['items']}
                print(f"   ✅ 已加载 {len(self.items_db)} 个物品")
        else:
            print(f"   ⚠️  数据库文件不存在，使用默认数据")
            self.items_db = self.create_default_database()
    
    def create_default_database(self):
        """创建默认物品数据库"""
        default_items = {
            # 突击步枪（从你的截图提取）
            'M7战斗步枪': {'value': 192324, 'rarity': 'epic', 'category': 'weapon'},
            'M7': {'value': 192324, 'rarity': 'epic', 'category': 'weapon'},
            'K437突击步枪': {'value': 85424, 'rarity': 'rare', 'category': 'weapon'},
            'K437': {'value': 85424, 'rarity': 'rare', 'category': 'weapon'},
            'MK47突击步枪': {'value': 90626, 'rarity': 'rare', 'category': 'weapon'},
            'MK47': {'value': 90626, 'rarity': 'rare', 'category': 'weapon'},
            'ASh-12战斗步枪': {'value': 90626, 'rarity': 'rare', 'category': 'weapon'},
            'ASh-12': {'value': 90626, 'rarity': 'rare', 'category': 'weapon'},
            'K416突击步枪': {'value': 201684, 'rarity': 'epic', 'category': 'weapon'},
            'K416': {'value': 201684, 'rarity': 'epic', 'category': 'weapon'},
            'AS Val突击步枪': {'value': 94271, 'rarity': 'rare', 'category': 'weapon'},
            'AS Val': {'value': 94271, 'rarity': 'rare', 'category': 'weapon'},
            'KC17突击步枪': {'value': 151911, 'rarity': 'epic', 'category': 'weapon'},
            'KC17': {'value': 151911, 'rarity': 'epic', 'category': 'weapon'},
            'M4A1突击步枪': {'value': 120688, 'rarity': 'rare', 'category': 'weapon'},
            'M4A1': {'value': 120688, 'rarity': 'rare', 'category': 'weapon'},
            'AUG突击步枪': {'value': 125374, 'rarity': 'rare', 'category': 'weapon'},
            'AUG': {'value': 125374, 'rarity': 'rare', 'category': 'weapon'},
            'AK-12突击步枪': {'value': 105477, 'rarity': 'rare', 'category': 'weapon'},
            'AK-12': {'value': 105477, 'rarity': 'rare', 'category': 'weapon'},
            'SCAR-H战斗步枪': {'value': 84270, 'rarity': 'rare', 'category': 'weapon'},
            'SCAR-H': {'value': 84270, 'rarity': 'rare', 'category': 'weapon'},
            'AKM突击步枪': {'value': 126187, 'rarity': 'rare', 'category': 'weapon'},
            'AKM': {'value': 126187, 'rarity': 'rare', 'category': 'weapon'},
            '腾龙突击步枪': {'value': 114167, 'rarity': 'rare', 'category': 'weapon'},
            '腾龙': {'value': 114167, 'rarity': 'rare', 'category': 'weapon'},
            'SG552突击步枪': {'value': 39059, 'rarity': 'common', 'category': 'weapon'},
            'SG552': {'value': 39059, 'rarity': 'common', 'category': 'weapon'},
            'G3战斗步枪': {'value': 39057, 'rarity': 'common', 'category': 'weapon'},
            'G3': {'value': 39057, 'rarity': 'common', 'category': 'weapon'},
            
            # 材料
            '曼德尔砖': {'value': 15000, 'rarity': 'legendary', 'category': 'material'},
            '电路板': {'value': 8000, 'rarity': 'rare', 'category': 'material'},
        }
        
        print(f"   ✅ 已加载 {len(default_items)} 个默认物品")
        return default_items
    
    def read_image_chinese_path(self, image_path):
        """读取中文路径图片"""
        try:
            img_array = np.fromfile(str(image_path), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img if img is not None else None
        except:
            return None
    
    def analyze_screenshot(self, image_path):
        """分析截图"""
        print(f"\n📸 分析截图：{Path(image_path).name}")
        
        img = self.read_image_chinese_path(image_path)
        
        if img is None:
            print(f"   ❌ 无法读取图片")
            return None
        
        print(f"   ✅ 图片尺寸：{img.shape[1]}x{img.shape[0]}")
        print(f"   🔍 OCR识别中...")
        
        result = self.analyze_all_text(img)
        
        if result and result['item_count'] > 0:
            self.display_results(result)
            return result
        else:
            print(f"   ℹ️  未识别到已知物品")
            return None
    
    def analyze_all_text(self, img):
        """分析图片中的所有文字"""
        try:
            ocr_results = self.ocr_reader.readtext(img)
        except Exception as e:
            print(f"   ❌ OCR失败：{e}")
            return None
        
        items = []
        
        for (bbox, text, confidence) in ocr_results:
            text = text.strip()
            
            if len(text) < 2 or confidence < 0.4:
                continue
            
            # 尝试匹配已知物品
            matched_item = self.match_item(text)
            
            if matched_item:
                print(f"   📦 识别到：{text} → {matched_item['name']} (置信度: {confidence:.2%})")
                
                items.append({
                    'name': matched_item['name'],
                    'value': matched_item['value'],
                    'rarity': matched_item['rarity'],
                    'confidence': confidence
                })
            else:
                # 【新增】检查是否是未知物品
                if self.is_potential_item(text):
                    self.record_unknown_item(text, confidence)
        
        if not items:
            return None
        
        unique_items = self.deduplicate_items(items)
        total_value = sum(item['value'] for item in unique_items)
        
        return {
            'items': unique_items,
            'total_value': total_value,
            'item_count': len(unique_items)
        }
    
    def match_item(self, text):
        """匹配物品"""
        # 精确匹配
        if text in self.items_db:
            return {'name': text, **self.items_db[text]}
        
        # 包含匹配
        for item_name in self.items_db.keys():
            if item_name in text or text in item_name:
                return {'name': item_name, **self.items_db[item_name]}
        
        return None
    
    def is_potential_item(self, text):
        """
        【新增】判断是否可能是物品
        """
        weapon_keywords = ['步枪', '突击', '战斗', '狙击', '手枪', '霰弹', '冲锋', 
                          '机枪', '榴弹', '火箭', '匕首', '刀', '剑']
        
        equipment_keywords = ['头盔', '护甲', '背包', '护目镜', '战术', '装备', 
                            '背心', '腰带', '手套']
        
        material_keywords = ['砖', '板', '金属', '芯片', '零件', '电路', '材料',
                           '合金', '晶体', '药剂']
        
        all_keywords = weapon_keywords + equipment_keywords + material_keywords
        
        # 包含关键词
        if any(kw in text for kw in all_keywords):
            return True
        
        # 武器型号格式（如AK-47、M4A1）
        if re.match(r'^[A-Z0-9\-]+$', text) and 2 <= len(text) <= 10:
            return True
        
        return False
    
    def record_unknown_item(self, text, confidence):
        """
        【新增】记录未知物品
        """
        # 去重
        if text not in [item['name'] for item in self.unknown_items]:
            self.unknown_items.append({
                'name': text,
                'confidence': confidence,
                'count': 1
            })
            print(f"   🆕 发现未知物品：{text} (置信度: {confidence:.2%})")
    
    def deduplicate_items(self, items):
        """去重"""
        unique = {}
        for item in items:
            name = item['name']
            if name not in unique or item['confidence'] > unique[name]['confidence']:
                unique[name] = item
        return list(unique.values())
    
    def display_results(self, result):
        """显示结果"""
        print("\n" + "="*60)
        print("📊 识别结果")
        print("="*60)
        
        rarity_symbols = {
            'common': '⚪', 'uncommon': '🟢', 'rare': '🔵',
            'epic': '🟣', 'legendary': '🟠', 'unknown': '❓'
        }
        
        for item in result['items']:
            symbol = rarity_symbols.get(item['rarity'], '❓')
            print(f"{symbol} {item['name']:<20} {item['value']:>10,} 币")
        
        print("-"*60)
        print(f"💰 总价值：{result['total_value']:,} 币")
        print(f"📦 物品数：{result['item_count']}")
        print("="*60)
    
    def batch_analyze(self, screenshots_folder):
        """批量分析"""
        folder = Path(screenshots_folder)
        screenshots = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
        
        if not screenshots:
            print(f"❌ 文件夹中没有找到截图：{screenshots_folder}")
            return
        
        print(f"📁 找到 {len(screenshots)} 张截图")
        
        all_results = []
        failed_screenshots = []
        
        for screenshot in screenshots:
            result = self.analyze_screenshot(screenshot)
            if result:
                all_results.append(result)
            else:
                failed_screenshots.append(screenshot.name)
        
        # 处理统计
        print(f"\n" + "="*60)
        print("📊 处理统计")
        print("="*60)
        print(f"总截图数：{len(screenshots)}")
        print(f"成功识别：{len(all_results)} ({len(all_results)/len(screenshots)*100:.1f}%)")
        print(f"未识别到：{len(failed_screenshots)} ({len(failed_screenshots)/len(screenshots)*100:.1f}%)")
        
        if all_results:
            self.display_summary(all_results)
        
        # 【新增】保存并显示未知物品
        if self.unknown_items:
            self.save_unknown_items()
            self.display_unknown_items()
            self.generate_pending_config()
    
    def display_summary(self, results):
        """汇总统计"""
        print("\n" + "="*60)
        print("📈 汇总统计")
        print("="*60)
        
        total_value = sum(r['total_value'] for r in results)
        total_items = sum(r['item_count'] for r in results)
        
        print(f"有效截图数：{len(results)}")
        print(f"识别物品数：{total_items}")
        print(f"总价值：{total_value:,} 币")
        print("="*60)
    
    def save_unknown_items(self):
        """
        【新增】保存未知物品
        """
        Path(self.unknown_items_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 读取已有记录
        existing = []
        if Path(self.unknown_items_file).exists():
            with open(self.unknown_items_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        # 合并
        for new_item in self.unknown_items:
            found = False
            for ex in existing:
                if ex['name'] == new_item['name']:
                    ex['count'] = ex.get('count', 0) + 1
                    ex['confidence'] = max(ex.get('confidence', 0), new_item['confidence'])
                    found = True
                    break
            if not found:
                existing.append(new_item)
        
        # 保存
        with open(self.unknown_items_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 已保存 {len(self.unknown_items)} 个未知物品到：{self.unknown_items_file}")
    
    def display_unknown_items(self):
        """
        【新增】显示未知物品报告
        """
        print("\n" + "="*60)
        print("🆕 发现的未知物品")
        print("="*60)
        print(f"本次发现 {len(self.unknown_items)} 个新物品：\n")
        
        for i, item in enumerate(self.unknown_items, 1):
            print(f"{i}. {item['name']} (置信度: {item['confidence']:.0%})")
        
        print("\n💡 下一步操作：")
        print("   1. 查看 data/unknown_items.json")
        print("   2. 查看 data/pending_items.txt（待填写配置）")
        print("   3. 填写价格后运行导入工具")
        print("="*60)
    
    def generate_pending_config(self):
        """
        【新增】生成待确认配置
        """
        config_file = "data/pending_items.txt"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("# 待添加的物品配置\n")
            f.write("# 格式：物品名称 | 价格 | 稀有度\n")
            f.write("# 稀有度选项：common, rare, epic, legendary\n")
            f.write("# 示例：新武器X | 50000 | rare\n\n")
            
            for item in self.unknown_items:
                f.write(f"{item['name']} | _____ | _____\n")
        
        print(f"📝 已生成待确认配置：{config_file}")


def main():
    """主函数"""
    print("="*60)
    print("🎮 三角洲行动 - 截图物品识别工具（自动学习版）")
    print("="*60)
    print()
    
    analyzer = ScreenshotAnalyzer()
    
    screenshots_folder = "D:/游戏截图/物品识别/"
    
    if not Path(screenshots_folder).exists():
        print(f"❌ 截图文件夹不存在")
        return
    
    analyzer.batch_analyze(screenshots_folder)
    
    print("\n✅ 分析完成！")


if __name__ == "__main__":
    main()