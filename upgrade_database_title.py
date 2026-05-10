#!/usr/bin/env python3
"""
数据库升级脚本 - 添加标题字段
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

    # 检查是否已经有 title 字段
    cursor.execute("PRAGMA table_info(notes)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'title' not in columns:
        try:
            cursor.execute('ALTER TABLE notes ADD COLUMN title TEXT')
            print("[OK] 添加字段: title")
        except Exception as e:
            print(f"[ERROR] 添加字段 title 失败: {e}")

    conn.commit()
    conn.close()
    print("\n数据库升级完成！")


if __name__ == '__main__':
    upgrade_database()
