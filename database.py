#!/usr/bin/env python3
"""
数据库模块 - SQLite 数据层
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re


def _row_to_dict(row) -> Dict:
    return {
        'id': str(row['id']),
        'content': row['content'],
        'timestamp': row['timestamp'],
        'source_type': row['source_type'] or 'text',
        'title': row['title'],
        'file_name': row['file_name'],
        'file_type': row['file_type'],
        'file_path': row['file_path']
    }


def _extract_keywords(question: str) -> List[str]:
    """从中文问句中提取有效关键词"""
    text = re.sub(r'[，。！？、；：“”‘’（）【】《》\s,.!?;:()\[\]{}]+', '', question)

    # 移除常见问句模式
    patterns = [
        '请问', '请告诉我', '能不能告诉我', '是否可以', '能告诉我',
        '帮我', '帮我看', '帮我看看', '帮我查', '帮我查查',
        '你知道', '你了解', '你知不知道', '是不是', '有没有',
        '是谁', '是什么', '在哪儿', '在哪里', '是哪', '是什么人',
        '怎么了', '什么样', '怎么', '如何', '为什么',
        '好不好', '行不行', '能不能', '可以吗', '对吗',
        '讲了什么', '说的是什么', '有吗', '了没',
        '有哪些', '有什么', '有没有什么', '介绍', '说一下', '说说',
        '告诉我', '列举', '列出', '包含', '包括', '还有哪些',
        '一下', '能不能', '可否', '麻烦',
    ]
    for pat in sorted(patterns, key=len, reverse=True):
        text = text.replace(pat, '')

    # 用停用字切分，得到多个关键词片段
    # 注意：不包含 "能"（属于 技能/能力 等真实词）、"有"（属于 有用/有人 等）
    stop_chars = set(
        '的了在和我或与就也都把从到让对给用这不它那'
        '请帮你他她吗呢吧啊哦嗯嘛谁什么怎么如何'
        '为什么哪可以是否关于是些个各每很太最更只'
        '但而所以因为虽然如果之'
        '这那各每所其者'
    )

    segments = []
    buf = []
    for ch in text:
        if ch in stop_chars:
            if len(buf) >= 2:
                segments.append(''.join(buf))
            buf = []
        else:
            buf.append(ch)
    if len(buf) >= 2:
        segments.append(''.join(buf))

    # 过滤太短的片段，同时把长词拆成 2-4 字 n-gram
    keywords = []
    for s in segments:
        if len(s) >= 2:
            keywords.append(s)
        # 长词拆成短词，提高匹配率
        if len(s) > 4:
            for win in [2, 3]:
                for i in range(len(s) - win + 1):
                    sub = s[i:i + win]
                    if sub not in keywords:
                        keywords.append(sub)

    return keywords if keywords else [question]


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
        if not keyword:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT id, content, timestamp, source_type, title, file_name, file_type, file_path
               FROM notes WHERE content LIKE ? OR title LIKE ? ORDER BY id DESC''',
            (f'%{keyword}%', f'%{keyword}%')
        )

        rows = cursor.fetchall()
        conn.close()

        return [_row_to_dict(row) for row in rows]

    def search_multi_keywords(self, question: str) -> List[Dict]:
        """从问句中提取关键词，分别搜索并合并结果"""
        if not question:
            return []

        keywords = _extract_keywords(question)
        if not keywords:
            return self.search_notes(question)[:5]

        seen = set()
        results = []
        for kw in keywords[:5]:
            for note in self.search_notes(kw):
                if note['id'] not in seen:
                    seen.add(note['id'])
                    results.append(note)

        return results[:10]

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
