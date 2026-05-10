#!/usr/bin/env python3
"""
数据库升级脚本 - 添加文件相关字段
"""

import sqlite3
from pathlib import Path


def upgrade_database():
    """升级数据库结构"""
    db_path = Path(__file__).parent / 'data' / 'notes.db'

    if not db_path.exists():
        print("数据库文件不存在")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查是否已经有这些字段
    cursor.execute("PRAGMA table_info(notes)")
    columns = [row[1] for row in cursor.fetchall()]

    fields_to_add = [
        ('source_type', "TEXT DEFAULT 'text'"),
        ('file_name', 'TEXT'),
        ('file_type', 'TEXT'),
        ('file_path', 'TEXT')
    ]

    for field_name, field_type in fields_to_add:
        if field_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE notes ADD COLUMN {field_name} {field_type}')
                print(f"[OK] 添加字段: {field_name}")
            except Exception as e:
                print(f"[ERROR] 添加字段 {field_name} 失败: {e}")

    conn.commit()
    conn.close()
    print("\n数据库升级完成！")


if __name__ == '__main__':
    upgrade_database()
