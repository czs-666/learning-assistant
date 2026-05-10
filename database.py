#!/usr/bin/env python3
"""
数据库模块 - SQLite 数据层
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """SQLite 数据库管理类"""

    def __init__(self, db_path: str = None):
        """初始化数据库连接"""
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'notes.db'

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)

        self._init_database()

    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_type TEXT DEFAULT 'text',
                title TEXT,
                file_name TEXT,
                file_type TEXT,
                file_path TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_note(self, content: str, source_type: str = 'text',
                 title: str = None, file_name: str = None, file_type: str = None,
                 file_path: str = None) -> Dict:
        """添加笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute(
            '''INSERT INTO notes (content, timestamp, source_type, title, file_name, file_type, file_path)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (content, timestamp, source_type, title, file_name, file_type, file_path)
        )

        note_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            'id': str(note_id),
            'content': content,
            'timestamp': timestamp,
            'source_type': source_type,
            'title': title,
            'file_name': file_name,
            'file_type': file_type,
            'file_path': file_path
        }

    def get_all_notes(self) -> List[Dict]:
        """获取所有笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, content, timestamp, source_type, title, file_name, file_type, file_path
            FROM notes ORDER BY id DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'id': str(row['id']),
                'content': row['content'],
                'timestamp': row['timestamp'],
                'source_type': row['source_type'] or 'text',
                'title': row['title'],
                'file_name': row['file_name'],
                'file_type': row['file_type'],
                'file_path': row['file_path']
            }
            for row in rows
        ]

    def search_notes(self, keyword: str) -> List[Dict]:
        """搜索笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT id, content, timestamp, source_type, title, file_name, file_type, file_path
               FROM notes WHERE content LIKE ? OR title LIKE ? ORDER BY id DESC''',
            (f'%{keyword}%', f'%{keyword}%')
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'id': str(row['id']),
                'content': row['content'],
                'timestamp': row['timestamp'],
                'source_type': row['source_type'] or 'text',
                'title': row['title'],
                'file_name': row['file_name'],
                'file_type': row['file_type'],
                'file_path': row['file_path']
            }
            for row in rows
        ]

    def update_note(self, note_id: str, content: str, title: str = None) -> Optional[Dict]:
        """更新笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute(
            'UPDATE notes SET content = ?, title = ?, timestamp = ? WHERE id = ?',
            (content, title, timestamp, int(note_id))
        )

        if cursor.rowcount == 0:
            conn.close()
            return None

        conn.commit()
        conn.close()

        return {
            'id': note_id,
            'content': content,
            'title': title,
            'timestamp': timestamp
        }

    def delete_note(self, note_id: str) -> bool:
        """删除笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM notes WHERE id = ?', (int(note_id),))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted
