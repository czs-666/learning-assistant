#!/usr/bin/env python3
"""
学习助手 - 个人知识库问答系统
"""

from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from werkzeug.utils import secure_filename
from database import Database
from file_handler import FileHandler
from ai_assistant import AIAssistant

app = Flask(__name__)

# 初始化 AI 助手
ai_assistant = None
try:
    # 从环境变量读取 API key
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if api_key:
        ai_assistant = AIAssistant(api_key=api_key)
        print("AI 助手初始化成功 (DeepSeek)")
    else:
        print("未设置 DEEPSEEK_API_KEY 环境变量，AI 功能将不可用")
except Exception as e:
    print(f"AI 助手初始化失败: {e}")

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
    """AI 智能问答"""
    if not request.json:
        return jsonify({'error': '无效的请求数据'}), 400

    question = (request.json.get('question') or '').strip()

    if not question:
        return jsonify({'error': '问题不能为空'}), 400

    # 检查 AI 助手是否可用
    if not ai_assistant:
        return jsonify({'error': 'AI 功能暂时不可用'}), 503

    try:
        # 从问句中提取关键词，搜索相关笔记作为上下文
        context_notes = db.search_multi_keywords(question)

        # 调用 AI 生成回答
        answer = ai_assistant.ask(question, context_notes)

        return jsonify({
            'answer': answer,
            'sources': context_notes
        })

    except Exception as e:
        print(f"AI 问答错误: {e}")
        return jsonify({'error': f'AI 回答失败: {str(e)}'}), 500


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

    # 获取原始文件名
    original_filename = file.filename
    print(f"[DEBUG] 原始文件名: {original_filename}")

    if not original_filename or original_filename == '':
        return jsonify({'error': '未获取到文件名'}), 400

    # 检查文件类型
    if not FileHandler.is_supported(original_filename):
        return jsonify({'error': f'不支持的文件格式：{original_filename}，仅支持 PDF、Word、TXT、Markdown'}), 400

    file_path = None
    try:
        # 保存文件 - 先获取扩展名
        original_filename = file.filename
        file_ext = Path(original_filename).suffix.lower()  # 获取扩展名（如 .pdf）

        # 使用 secure_filename 处理文件名
        filename = secure_filename(original_filename)
        print(f"[DEBUG] 安全文件名: {filename}")

        # 如果 secure_filename 返回空（中文文件名会被清空），使用时间戳+扩展名
        if not filename or filename == '':
            filename = f"upload{file_ext}"
            print(f"[DEBUG] 文件名为空，使用默认名称: {filename}")

        # 确保文件名有扩展名
        if not filename.endswith(file_ext):
            filename = Path(filename).stem + file_ext
            print(f"[DEBUG] 添加扩展名后: {filename}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = app.config['UPLOAD_FOLDER'] / unique_filename
        print(f"[DEBUG] 保存路径: {file_path}")
        file.save(file_path)

        # 提取文本
        text_content, file_type = FileHandler.extract_text(str(file_path))

        # 使用原始文件名（去掉扩展名）作为标题
        title = Path(original_filename).stem
        print(f"[DEBUG] 笔记标题: {title}")

        # 保存到数据库
        note = db.add_note(
            content=text_content,
            source_type='file',
            title=title,
            file_name=original_filename,  # 保存原始文件名
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
        error_msg = f"上传错误: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())

        # 同时写入日志文件
        with open('upload_error.log', 'a', encoding='utf-8') as log:
            log.write(f"\n{'='*50}\n")
            log.write(f"Time: {datetime.now()}\n")
            log.write(f"Error: {str(e)}\n")
            log.write(traceback.format_exc())

        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
