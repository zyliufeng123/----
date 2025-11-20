"""
价格自动采集与追踪系统
"""

import cv2
import numpy as np
from pathlib import Path
import json
import easyocr
from PIL import Image
import re
from datetime import datetime

class PriceTracker:
    """
    价格追踪器
    - 自动从截图提取物品名称和价格
    - 记录价格历史
    - 分析价格趋势
    """
    
    def __init__(self):
        print("🔧 初始化价格追踪系统...")
        
        # OCR引擎
        print("   加载OCR引擎...")
        self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        
        # 价格数据库文件
        self.price_db_file = "data/price_history.json"
        self.current_prices_file = "data/current_prices.json"
        
        # 加载历史数据
        self.load_price_history()
        
        print("✅ 初始化完成！\n")
    
    def load_price_history(self):
        """加载价格历史数据"""
        if Path(self.price_db_file).exists():
            with open(self.price_db_file, 'r', encoding='utf-8') as f:
                self.price_history = json.load(f)
            print(f"   ✅ 已加载 {len(self.price_history)} 个物品的历史价格")
        else:
            self.price_history = {}
            print("   ℹ️  价格历史数据库为空，开始新记录")
    
    def read_image_chinese_path(self, image_path):
        """读取中文路径图片"""
        try:
            img_array = np.fromfile(str(image_path), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img if img is not None else None
        except:
            return None
    
    def analyze_market_screenshot(self, image_path):
        """
        分析交易行截图，提取物品和价格
        
        返回：[
            {'name': 'M4A1突击步枪', 'price': 120688, 'confidence': 0.95},
            ...
        ]
        """
        print(f"\n📸 分析截图：{Path(image_path).name}")
        
        img = self.read_image_chinese_path(image_path)
        
        if img is None:
            print(f"   ❌ 无法读取图片")
            return []
        
        print(f"   ✅ 图片尺寸：{img.shape[1]}x{img.shape[0]}")
        
        # 检测是否是交易行界面
        if not self.is_market_interface(img):
            print(f"   ℹ️  非交易行界面，跳过")
            return []
        
        print(f"   🏪 检测到交易行界面")
        print(f"   🔍 OCR识别中...")
        
        # OCR识别
        ocr_results = self.ocr_reader.readtext(img)
        
        # 提取物品和价格
        items_with_prices = self.extract_items_and_prices(ocr_results)
        
        return items_with_prices
    
    def is_market_interface(self, img):
        """检测是否是交易行界面"""
        height, width = img.shape[:2]
        top_region = img[0:int(height*0.15), :]
        
        try:
            results = self.ocr_reader.readtext(top_region)
            texts = [text for (_, text, _) in results]
            
            keywords = ['交易行', '仓库', '特勤处', '开始游戏', '装备', '武器', '枪械']
            
            for text in texts:
                if any(kw in text for kw in keywords):
                    return True
        except:
            pass
        
        return False
    
    def extract_items_and_prices(self, ocr_results):
        """
        从OCR结果中提取物品名称和对应价格
        
        策略：
        1. 识别所有文字和位置
        2. 将物品名称和价格配对（基于位置关系）
        3. 验证价格合理性
        """
        items_with_prices = []
        
        # 分离物品名称和数字
        item_candidates = []  # 可能是物品名称的文本
        price_candidates = []  # 可能是价格的数字
        
        for (bbox, text, confidence) in ocr_results:
            text = text.strip()
            
            # 跳过过短或置信度低的
            if len(text) < 2 or confidence < 0.4:
                continue
            
            # 提取中心坐标
            center_x = sum([p[0] for p in bbox]) / 4
            center_y = sum([p[1] for p in bbox]) / 4
            
            # 判断是物品名称还是价格
            if self.is_item_name(text):
                item_candidates.append({
                    'text': text,
                    'x': center_x,
                    'y': center_y,
                    'confidence': confidence,
                    'bbox': bbox
                })
            
            # 提取数字（可能是价格）
            numbers = self.extract_numbers(text)
            if numbers:
                for num in numbers:
                    price_candidates.append({
                        'price': num,
                        'x': center_x,
                        'y': center_y,
                        'confidence': confidence
                    })
        
        print(f"   找到 {len(item_candidates)} 个物品候选")
        print(f"   找到 {len(price_candidates)} 个价格候选")
        
        # 为每个物品匹配最近的价格
        for item in item_candidates:
            matched_price = self.find_nearest_price(item, price_candidates)
            
            if matched_price:
                items_with_prices.append({
                    'name': item['text'],
                    'price': matched_price['price'],
                    'confidence': min(item['confidence'], matched_price['confidence']),
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"   💰 {item['text']:<20} {matched_price['price']:>10,} 币")
        
        return items_with_prices
    
    def is_item_name(self, text):
        """判断文本是否是物品名称"""
        weapon_keywords = ['步枪', '突击', '战斗', '狙击', '手枪', '霰弹', '冲锋', 
                          '机枪', '榴弹', '火箭', '匕首', '刀']
        
        equipment_keywords = ['头盔', '护甲', '背包', '护目镜', '战术', '装备', 
                            '背心', '腰带', '手套', '靴子']
        
        material_keywords = ['砖', '板', '金属', '芯片', '零件', '电路', '材料',
                           '合金', '晶体', '药剂', '文件', '情报']
        
        all_keywords = weapon_keywords + equipment_keywords + material_keywords
        
        # 包含关键词
        if any(kw in text for kw in all_keywords):
            return True
        
        # 武器型号格式
        if re.match(r'^[A-Z0-9\-]+$', text) and 2 <= len(text) <= 10:
            return True
        
        return False
    
    def extract_numbers(self, text):
        """
        从文本中提取数字（价格）
        
        支持格式：
        - 12,345
        - 12345
        - 12.345 (欧洲格式)
        """
        numbers = []
        
        # 移除逗号和点
        cleaned = text.replace(',', '').replace('.', '')
        
        # 提取纯数字
        matches = re.findall(r'\d+', cleaned)
        
        for match in matches:
            try:
                num = int(match)
                
                # 价格合理性检查（游戏内价格通常在100-1000000之间）
                if 100 <= num <= 1000000:
                    numbers.append(num)
            except:
                pass
        
        return numbers
    
    def find_nearest_price(self, item, price_candidates):
        """
        为物品找到最近的价格
        
        策略：
        1. 优先找右侧的价格（交易行通常在右边显示价格）
        2. 垂直距离要近（同一行）
        3. 水平距离合理（不要太远）
        """
        if not price_candidates:
            return None
        
        best_match = None
        best_score = float('inf')
        
        for price in price_candidates:
            # 计算距离
            dx = price['x'] - item['x']
            dy = abs(price['y'] - item['y'])
            
            # 价格应该在物品右侧
            if dx < 0:
                continue
            
            # 垂直距离要小（同一行）
            if dy > 50:  # 像素阈值
                continue
            
            # 水平距离合理（不要太远）
            if dx > 800:  # 像素阈值
                continue
            
            # 综合评分（垂直距离权重更高）
            score = dy * 3 + dx * 0.5
            
            if score < best_score:
                best_score = score
                best_match = price
        
        return best_match
    
    def record_prices(self, items_with_prices):
        """
        记录价格到历史数据库
        """
        if not items_with_prices:
            return
        
        timestamp = datetime.now().isoformat()
        
        for item in items_with_prices:
            name = item['name']
            price = item['price']
            
            # 初始化物品记录
            if name not in self.price_history:
                self.price_history[name] = {
                    'name': name,
                    'prices': [],
                    'first_seen': timestamp,
                    'last_update': timestamp
                }
            
            # 添加价格记录
            self.price_history[name]['prices'].append({
                'price': price,
                'timestamp': timestamp,
                'confidence': item['confidence']
            })
            
            self.price_history[name]['last_update'] = timestamp
            
            # 只保留最近100条记录（避免文件过大）
            if len(self.price_history[name]['prices']) > 100:
                self.price_history[name]['prices'] = \
                    self.price_history[name]['prices'][-100:]
        
        # 保存到文件
        self.save_price_history()
        
        # 更新当前价格表
        self.update_current_prices()
        
        print(f"\n💾 已记录 {len(items_with_prices)} 个物品的价格")
    
    def save_price_history(self):
        """保存价格历史"""
        Path(self.price_db_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.price_db_file, 'w', encoding='utf-8') as f:
            json.dump(self.price_history, f, ensure_ascii=False, indent=2)
    
    def update_current_prices(self):
        """
        更新当前价格表（用于快速查询）
        
        包含：
        - 最新价格
        - 最低价
        - 最高价
        - 平均价
        - 价格趋势
        """
        current_prices = {}
        
        for name, data in self.price_history.items():
            prices = [p['price'] for p in data['prices']]
            
            if not prices:
                continue
            
            latest_price = prices[-1]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            # 计算趋势（最近5次 vs 之前平均）
            recent_prices = prices[-5:] if len(prices) >= 5 else prices
            recent_avg = sum(recent_prices) / len(recent_prices)
            
            if len(prices) > 5:
                old_avg = sum(prices[:-5]) / len(prices[:-5])
                trend_percent = ((recent_avg - old_avg) / old_avg) * 100
                
                if trend_percent > 5:
                    trend = 'rising'  # 上涨
                elif trend_percent < -5:
                    trend = 'falling'  # 下跌
                else:
                    trend = 'stable'  # 稳定
            else:
                trend = 'unknown'
            
            current_prices[name] = {
                'name': name,
                'latest_price': latest_price,
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': int(avg_price),
                'trend': trend,
                'sample_count': len(prices),
                'last_update': data['last_update']
            }
        
        # 保存当前价格表
        with open(self.current_prices_file, 'w', encoding='utf-8') as f:
            json.dump(current_prices, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已更新当前价格表：{self.current_prices_file}")
    
    def batch_analyze(self, screenshots_folder):
        """批量分析截图文件夹"""
        folder = Path(screenshots_folder)
        screenshots = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
        
        if not screenshots:
            print(f"❌ 文件夹中没有找到截图：{screenshots_folder}")
            return
        
        print(f"📁 找到 {len(screenshots)} 张截图")
        
        all_items = []
        
        for screenshot in screenshots:
            items = self.analyze_market_screenshot(screenshot)
            
            if items:
                all_items.extend(items)
                # 实时记录（避免数据丢失）
                self.record_prices(items)
        
        # 显示汇总
        if all_items:
            self.display_summary(all_items)
            self.display_price_analysis()
        else:
            print("\n⚠️  没有识别到任何物品价格")
    
    def display_summary(self, items):
        """显示采集汇总"""
        print("\n" + "="*60)
        print("📊 采集汇总")
        print("="*60)
        
        unique_items = {}
        for item in items:
            name = item['name']
            if name not in unique_items:
                unique_items[name] = []
            unique_items[name].append(item['price'])
        
        print(f"采集物品种类：{len(unique_items)}")
        print(f"总价格记录数：{len(items)}")
        print("="*60)
    
    def display_price_analysis(self):
        """显示价格分析报告"""
        print("\n" + "="*60)
        print("📈 价格分析报告")
        print("="*60)
        
        # 读取当前价格表
        if not Path(self.current_prices_file).exists():
            print("暂无价格数据")
            return
        
        with open(self.current_prices_file, 'r', encoding='utf-8') as f:
            current_prices = json.load(f)
        
        # 按价格排序
        sorted_items = sorted(
            current_prices.values(),
            key=lambda x: x['latest_price'],
            reverse=True
        )
        
        print(f"\n🏆 最贵的10个物品：")
        print("-"*60)
        
        trend_symbols = {
            'rising': '📈',
            'falling': '📉',
            'stable': '➡️',
            'unknown': '❓'
        }
        
        for i, item in enumerate(sorted_items[:10], 1):
            trend = trend_symbols.get(item['trend'], '❓')
            
            print(f"{i:2d}. {item['name']:<20}")
            print(f"    当前: {item['latest_price']:>8,} 币  {trend}")
            print(f"    最低: {item['min_price']:>8,} 币")
            print(f"    最高: {item['max_price']:>8,} 币")
            print(f"    平均: {item['avg_price']:>8,} 币")
            print(f"    样本: {item['sample_count']} 次")
            print()
        
        print("="*60)


def main():
    """主函数"""
    print("="*60)
    print("🎮 三角洲行动 - 价格自动采集系统")
    print("="*60)
    print()
    
    tracker = PriceTracker()
    
    screenshots_folder = "D:/游戏截图/物品识别/"
    
    if not Path(screenshots_folder).exists():
        print(f"❌ 截图文件夹不存在")
        return
    
    tracker.batch_analyze(screenshots_folder)
    
    print("\n✅ 采集完成！")
    print("\n💡 生成的文件：")
    print(f"   📊 价格历史：data/price_history.json")
    print(f"   💰 当前价格：data/current_prices.json")


if __name__ == "__main__":
    main()