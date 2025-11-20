"""
自动模板提取工具 - B方案
功能：从原始截图中提取小地图、UI等模板
"""

import cv2
import os
import numpy as np
from pathlib import Path

class TemplateExtractor:
    def __init__(self, raw_path, output_path):
        self.raw_path = raw_path
        self.output_path = output_path
        
        # 固定区域定义（需要根据你的屏幕分辨率调整）
        self.regions = {
            'minimap': {'x': 30, 'y': 30, 'w': 280, 'h': 280},  # 左上角小地图
            'ui': {'x': 860, 'y': 400, 'w': 200, 'h': 150},     # 中央UI提示
        }
    
    def extract_minimaps(self, game_id):
        """提取小地图"""
        print(f"\n🔍 正在提取小地图（游戏{game_id}）...")
        
        raw_dir = os.path.join(self.raw_path, game_id)
        output_dir = os.path.join(self.output_path, 'minimap')
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(raw_dir):
            print(f"❌ 找不到目录：{raw_dir}")
            return
        
        files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.png')])
        
        if not files:
            print("❌ 没有找到截图文件")
            return
        
        # 每隔10张提取一张（避免重复）
        selected_files = files[::10]
        
        count = 0
        for filename in selected_files:
            filepath = os.path.join(raw_dir, filename)
            img = cv2.imread(filepath)
            
            if img is None:
                continue
            
            # 裁剪小地图区域
            r = self.regions['minimap']
            minimap = img[r['y']:r['y']+r['h'], r['x']:r['x']+r['w']]
            
            # 检查是否有效（不是全黑）
            if minimap.mean() > 10:
                output_file = os.path.join(output_dir, f"{game_id}_minimap_{count:03d}.png")
                cv2.imwrite(output_file, minimap)
                count += 1
        
        print(f"✅ 提取了 {count} 张小地图")
    
    def extract_ui(self, game_id):
        """提取UI元素"""
        print(f"\n🔍 正在提取UI元素（游戏{game_id}）...")
        
        raw_dir = os.path.join(self.raw_path, game_id)
        output_dir = os.path.join(self.output_path, 'ui')
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(raw_dir):
            return
        
        files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.png')])
        
        count = 0
        for filename in files:
            filepath = os.path.join(raw_dir, filename)
            img = cv2.imread(filepath)
            
            if img is None:
                continue
            
            # 裁剪UI区域
            r = self.regions['ui']
            ui_crop = img[r['y']:r['y']+r['h'], r['x']:r['x']+r['w']]
            
            # 检测是否有UI（亮度变化大）
            gray = cv2.cvtColor(ui_crop, cv2.COLOR_BGR2GRAY)
            if gray.std() > 30:  # 有明显对比度
                output_file = os.path.join(output_dir, f"{game_id}_ui_{count:03d}.png")
                cv2.imwrite(output_file, ui_crop)
                count += 1
        
        print(f"✅ 提取了 {count} 张UI元素")
    
    def process_game(self, game_id):
        """处理单局游戏"""
        print(f"\n{'='*50}")
        print(f"处理游戏：{game_id}")
        print(f"{'='*50}")
        
        self.extract_minimaps(game_id)
        self.extract_ui(game_id)

def main():
    import sys
    
    extractor = TemplateExtractor(
        raw_path="data_collection/raw_screenshots",
        output_path="data_collection/templates"
    )
    
    if len(sys.argv) < 2:
        # 自动处理所有游戏
        raw_dir = "data_collection/raw_screenshots"
        if os.path.exists(raw_dir):
            games = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
            
            if not games:
                print("❌ 没有找到游戏数据")
                return
            
            print(f"找到 {len(games)} 个游戏数据")
            for game_id in games:
                extractor.process_game(game_id)
            
            print(f"\n{'='*50}")
            print("🎉 所有数据处理完成！")
            print(f"{'='*50}")
        else:
            print("❌ 找不到数据目录")
    else:
        game_id = sys.argv[1]
        extractor.process_game(game_id)

if __name__ == "__main__":
    main()