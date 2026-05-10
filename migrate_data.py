#!/usr/bin/env python3
"""
数据迁移脚本 - 从 JSON 迁移到 SQLite
"""

import json
from pathlib import Path
from database import Database


def migrate():
    """执行数据迁移"""
    json_file = Path(__file__).parent / 'data' / 'notes.json'

    # 检查 JSON 文件是否存在
    if not json_file.exists():
        print("未找到 notes.json 文件，无需迁移")
        return

    # 读取 JSON 数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    notes = data.get('notes', [])

    if not notes:
        print("JSON 文件中没有笔记数据")
        return

    print(f"找到 {len(notes)} 条笔记，开始迁移...")

    # 初始化数据库
    db = Database()

    # 迁移数据
    migrated = 0
    for note in notes:
        try:
            db.add_note(note['content'])
            migrated += 1
            print(f"已迁移: {migrated}/{len(notes)}")
        except Exception as e:
            print(f"迁移失败: {e}")

    print(f"\n迁移完成！成功迁移 {migrated} 条笔记")

    # 备份原 JSON 文件
    backup_file = json_file.parent / 'notes.json.backup'
    json_file.rename(backup_file)
    print(f"原 JSON 文件已备份为: {backup_file}")


if __name__ == '__main__':
    migrate()
