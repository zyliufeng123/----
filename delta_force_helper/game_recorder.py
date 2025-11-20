"""
游戏数据记录工具 - B方案
功能：按快捷键记录开箱、遭遇、死亡
"""

from pynput import keyboard
import json
import time
import os
from datetime import datetime

class GameRecorder:
    def __init__(self, save_path):
        self.save_path = save_path
        self.game_data = {
            'game_id': f"game_{int(time.time())}",
            'start_time': datetime.now().isoformat(),
            'spawn_point': None,
            'loots': [],
            'encounters': [],
            'death': None
        }
        self.listener = None
        self.game_start_time = time.time()
        
        os.makedirs(save_path, exist_ok=True)
    
    def _get_game_time(self):
        """获取游戏内时间（分钟）"""
        elapsed = time.time() - self.game_start_time
        return round(elapsed / 60, 1)
    
    def _on_press(self, key):
        """按键回调"""
        try:
            # F9: 记录开箱
            if key == keyboard.Key.f9:
                self._record_loot()
            
            # F10: 记录遭遇
            elif key == keyboard.Key.f10:
                self._record_encounter()
            
            # F11: 记录死亡（并自动保存）
            elif key == keyboard.Key.f11:
                self._record_death()
                self.save()
                return False  # 停止监听
            
            # ESC: 手动保存并退出
            elif key == keyboard.Key.esc:
                print("\n\n⏸️  手动停止")
                self.save()
                return False
                
        except AttributeError:
            pass
    
    def _record_loot(self):
        """记录开箱"""
        print("\n" + "="*50)
        print("🎁 记录开箱")
        print("="*50)
        
        container = input("容器名称（例如：C3保险柜）：").strip()
        if not container:
            print("❌ 已取消")
            return
        
        try:
            value = int(input("出货价值（金币）：").strip())
        except ValueError:
            print("❌ 价值必须是数字")
            return
        
        game_time = self._get_game_time()
        
        self.game_data['loots'].append({
            'container': container,
            'value': value,
            'time': game_time,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"✅ 已记录：{container} - {value}币 (游戏时间{game_time}分钟)")
        print("继续游戏...\n")
    
    def _record_encounter(self):
        """记录遭遇"""
        print("\n" + "="*50)
        print("⚔️  记录遭遇")
        print("="*50)
        
        location = input("位置（例如：C3二楼）：").strip()
        if not location:
            print("❌ 已取消")
            return
        
        print("结果：1=逃脱  2=击杀敌人  3=被击杀")
        result_map = {'1': 'escape', '2': 'kill', '3': 'death'}
        result_input = input("选择（1/2/3）：").strip()
        result = result_map.get(result_input, 'unknown')
        
        game_time = self._get_game_time()
        
        self.game_data['encounters'].append({
            'location': location,
            'result': result,
            'time': game_time,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"✅ 已记录遭遇：{location} - {result}")
        print("继续游戏...\n")
    
    def _record_death(self):
        """记录死亡"""
        print("\n" + "="*50)
        print("💀 记录死亡")
        print("="*50)
        
        location = input("死亡位置（例如：D2走廊）：").strip()
        cause = input("死因（例如：被偷袭）：").strip()
        
        game_time = self._get_game_time()
        
        self.game_data['death'] = {
            'location': location,
            'cause': cause,
            'time': game_time,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 已记录死亡：{location}")
    
    def save(self):
        """保存数据"""
        filename = f"{self.game_data['game_id']}.json"
        filepath = os.path.join(self.save_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.game_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存：{filename}")
        print(f"📊 统计：")
        print(f"   - 开箱记录：{len(self.game_data['loots'])}次")
        print(f"   - 遭遇记录：{len(self.game_data['encounters'])}次")
        print(f"   - 游戏时长：{self._get_game_time()}分钟")
    
    def start(self):
        """开始监听"""
        print("="*50)
        print("🎮 游戏数据记录器")
        print("="*50)
        print("\n快捷键说明：")
        print("  F9  - 记录开箱")
        print("  F10 - 记录遭遇")
        print("  F11 - 记录死亡（自动保存并退出）")
        print("  ESC - 手动保存并退出")
        print("\n✅ 记录器已启动，请开始游戏\n")
        
        with keyboard.Listener(on_press=self._on_press) as listener:
            self.listener = listener
            listener.join()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法：")
        print("  python game_recorder.py start")
        return
    
    command = sys.argv[1]
    
    if command == "start":
        recorder = GameRecorder("data_collection/records")
        recorder.start()
    else:
        print(f"❌ 未知命令：{command}")

if __name__ == "__main__":
    main()