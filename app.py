#!/usr/bin/env python3
"""
学习助手 - 个人知识库问答系统
"""

from flask import Flask, render_template, request, jsonify
import os
import json
from pathlib import Path
from anthropic import Anthropic
from datetime import datetime

app = Flask(__name__)

# 数据文件路径
DATA_FILE = Path(__file__).parent / 'data' / 'notes.json'
DATA_FILE.parent.mkdir(exist_ok=True)

# 初始化 Anthropic 客户端
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("警告: 未设置 ANTHROPIC_API_KEY 环境变量")
client = Anthropic(api_key=api_key) if api_key else None


def load_notes():
    """加载笔记数据"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'notes': []}


def save_notes(data):
    """保存笔记数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def search_notes(keyword):
    """搜索笔记"""
    data = load_notes()
    keyword_lower = keyword.lower()
    results = []

    for note in data['notes']:
        if keyword_lower in note['content'].lower() or keyword_lower in note.get('title', '').lower():
            results.append(note)

    return results


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/notes', methods=['GET', 'POST'])
def notes():
    """获取所有笔记或添加笔记"""
    if request.method == 'GET':
        data = load_notes()
        return jsonify(data)

    # POST - 添加笔记
    content = request.json.get('content', '').strip()

    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    data = load_notes()

    note = {
        'id': str(len(data['notes']) + 1),
        'content': content,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    data['notes'].append(note)
    save_notes(data)

    return jsonify({'success': True, 'note': note})


@app.route('/api/search', methods=['GET'])
def search():
    """搜索笔记"""
    keyword = request.args.get('q', '').strip()

    if not keyword:
        return jsonify({'results': []})

    results = search_notes(keyword)
    return jsonify({'results': results})


@app.route('/api/ask', methods=['POST'])
def ask():
    """问答"""
    question = request.json.get('question', '').strip()

    if not question:
        return jsonify({'error': '问题不能为空'}), 400

    if not client:
        return jsonify({'error': '未配置 API Key'}), 500

    # 搜索相关笔记
    results = search_notes(question)[:3]

    if not results:
        return jsonify({
            'answer': '抱歉，我在你的笔记中没有找到相关内容。\n\n建议：\n- 尝试用不同的关键词提问\n- 先添加相关的学习笔记',
            'sources': [],
            'no_results': True
        })

    # 构建上下文
    context = "\n\n".join([f"笔记 {i+1}:\n{note['content']}" for i, note in enumerate(results)])

    # 调用 Claude
    try:
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1500,
            system=f"""你是一个学习助手。用户会问关于他学习笔记的问题。

重要规则：
1. 只基于提供的笔记内容回答问题
2. 如果笔记中没有相关信息，明确说"笔记中没有找到相关内容"
3. 不要凭空编造或使用笔记外的知识
4. 回答时引用具体的笔记内容

用户的笔记：
{context}""",
            messages=[{
                'role': 'user',
                'content': question
            }]
        )

        answer = response.content[0].text

        return jsonify({
            'answer': answer,
            'sources': results
        })

    except Exception as e:
        return jsonify({'error': f'API 调用失败: {str(e)}'}), 500


@app.route('/api/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    """更新笔记"""
    content = request.json.get('content', '').strip()

    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    data = load_notes()

    for note in data['notes']:
        if note['id'] == note_id:
            note['content'] = content
            note['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_notes(data)
            return jsonify({'success': True, 'note': note})

    return jsonify({'error': '笔记不存在'}), 404


@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除笔记"""
    data = load_notes()

    original_length = len(data['notes'])
    data['notes'] = [note for note in data['notes'] if note['id'] != note_id]

    if len(data['notes']) == original_length:
        return jsonify({'error': '笔记不存在'}), 404

    save_notes(data)
    return jsonify({'success': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
