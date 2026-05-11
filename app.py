#!/usr/bin/env python3
"""
学习助手 - 个人知识库问答系统
"""

from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from database import Database
from file_handler import FileHandler

app = Flask(__name__)

# 配置文件上传
UPLOAD_FOLDER = Path(__file__).parent / 'data' / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB 最大文件大小

# 初始化数据库
db = Database()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/notes', methods=['GET', 'POST'])
def notes():
    """获取所有笔记或添加笔记"""
    if request.method == 'GET':
        all_notes = db.get_all_notes()
        return jsonify({'notes': all_notes})

    # POST - 添加笔记
    if not request.json:
        return jsonify({'error': '无效的请求数据'}), 400

    content = (request.json.get('content') or '').strip()
    title = (request.json.get('title') or '').strip()

    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    note = db.add_note(content, title=title if title else None)
    return jsonify({'success': True, 'note': note})


@app.route('/api/search', methods=['GET'])
def search():
    """搜索笔记"""
    keyword = request.args.get('q', '').strip()

    if not keyword:
        return jsonify({'results': []})

    results = db.search_notes(keyword)
    return jsonify({'results': results})


@app.route('/api/ask', methods=['POST'])
def ask():
    """搜索笔记"""
    if not request.json:
        return jsonify({'error': '无效的请求数据'}), 400

    keyword = (request.json.get('question') or '').strip()

    if not keyword:
        return jsonify({'error': '关键词不能为空'}), 400

    # 搜索相关笔记
    results = db.search_notes(keyword)

    return jsonify({'results': results})


@app.route('/api/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    """更新笔记"""
    if not request.json:
        return jsonify({'error': '无效的请求数据'}), 400

    content = (request.json.get('content') or '').strip()
    title = (request.json.get('title') or '').strip()

    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    note = db.update_note(note_id, content, title if title else None)

    if note is None:
        return jsonify({'error': '笔记不存在'}), 404

    return jsonify({'success': True, 'note': note})


@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除笔记"""
    deleted = db.delete_note(note_id)

    if not deleted:
        return jsonify({'error': '笔记不存在'}), 404

    return jsonify({'success': True})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件并提取文本"""
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    # 检查文件类型
    if not FileHandler.is_supported(file.filename):
        return jsonify({'error': '不支持的文件格式，仅支持 PDF、Word、TXT、Markdown'}), 400

    file_path = None
    try:
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = app.config['UPLOAD_FOLDER'] / unique_filename
        file.save(file_path)

        # 提取文本
        text_content, file_type = FileHandler.extract_text(str(file_path))

        # 使用文件名（去掉扩展名）作为标题
        title = Path(filename).stem

        # 保存到数据库
        note = db.add_note(
            content=text_content,
            source_type='file',
            title=title,
            file_name=filename,
            file_type=file_type,
            file_path=str(file_path)
        )

        return jsonify({'success': True, 'note': note})

    except Exception as e:
        # 如果出错，删除已保存的文件
        if file_path and file_path.exists():
            file_path.unlink()

        # 打印详细错误信息到控制台
        import traceback
        print(f"上传错误: {str(e)}")
        print(traceback.format_exc())

        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
