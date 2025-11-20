"""
自动截图工具 - B方案（修复版）
功能：后台自动截图，不影响游戏
"""

import cv2
import numpy as np
import time
import os
from datetime import datetime
import threading
from PIL import ImageGrab

class AutoCapture:
    def __init__(self, save_path, interval=3):
        """
        save_path: 保存路径
        interval: 截图间隔（秒）
        """
        self.save_path = save_path
        self.interval = interval
        self.is_running = False
        self.frame_count = 0
        self.thread = None
        
    def _capture_loop(self):
        """截图循环"""
        print(f"✅ 自动截图已启动（每{self.interval}秒一次）")
        print(f"📁 保存位置：{self.save_path}")
        print("⏸️  按 Ctrl+C 停止\n")
        
        while self.is_running:
            try:
                # 使用PIL截图（更稳定）
                screenshot = ImageGrab.grab()
                
                # 转换为numpy数组
                img = np.array(screenshot)
                
                # 转换颜色格式（RGB -> BGR）
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # 生成文件名
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"frame_{self.frame_count:04d}_{timestamp}.png"
                filepath = os.path.join(self.save_path, filename)
                
                # 保存
                cv2.imwrite(filepath, img)
                
                self.frame_count += 1
                print(f"📸 已截图：{filename} (总计{self.frame_count}张)", end='\r')
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"\n❌ 截图出错：{e}")
                print("💡 尝试继续...")
                time.sleep(1)
    
    def start(self):
        """开始截图"""
        if self.is_running:
            print("⚠️  已在运行中")
            return
        
        # 确保保存目录存在
        os.makedirs(self.save_path, exist_ok=True)
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """停止截图"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        print(f"\n⏹️  截图已停止，共保存 {self.frame_count} 张")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法：")
        print("  启动：python auto_capture.py start [游戏编号]")
        print("  示例：python auto_capture.py start game001")
        return
    
    command = sys.argv[1]
    
    if command == "start":
        game_id = sys.argv[2] if len(sys.argv) > 2 else f"game{int(time.time())}"
        save_path = f"data_collection/raw_screenshots/{game_id}"
        
        capturer = AutoCapture(save_path, interval=3)
        capturer.start()
        
        try:
            # 保持运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            capturer.stop()
            print("\n✅ 程序已退出")
    else:
        print(f"❌ 未知命令：{command}")

if __name__ == "__main__":
    main()