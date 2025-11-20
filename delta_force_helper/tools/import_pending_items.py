import json
from pathlib import Path

def import_pending_items():
    """导入待确认的物品"""
    
    pending_file = "data/pending_items.txt"
    db_file = "data/items/items_database.json"
    
    if not Path(pending_file).exists():
        print("❌ 没有找到待导入文件")
        return
    
    # 读取待导入项
    new_items = []
    
    with open(pending_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 解析：物品名 | 价格 | 稀有度
            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) != 3:
                continue
            
            name, price, rarity = parts
            
            # 检查是否填写完整
            if '_' in price or '_' in rarity:
                print(f"⚠️  跳过未填写完整的：{name}")
                continue
            
            try:
                new_items.append({
                    'name': name,
                    'value': int(price),
                    'rarity': rarity,
                    'category': 'weapon'  # 可以自动判断或手动指定
                })
                print(f"✅ 准备导入：{name} - {price} 币")
            except:
                print(f"❌ 格式错误：{line}")
    
    if not new_items:
        print("\n❌ 没有有效的待导入物品")
        return
    
    # 读取现有数据库
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    
    if Path(db_file).exists():
        with open(db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
    else:
        db = {'items': []}
    
    # 添加新物品
    for item in new_items:
        # 检查是否已存在
        exists = any(i['name'] == item['name'] for i in db['items'])
        
        if not exists:
            db['items'].append(item)
    
    # 保存
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 成功导入 {len(new_items)} 个物品！")
    print(f"💾 已保存到：{db_file}")

if __name__ == "__main__":
    import_pending_items()