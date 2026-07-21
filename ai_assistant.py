#!/usr/bin/env python3
"""
AI 助手模块 - 使用 DeepSeek API 进行智能问答
"""

import os
import json
import subprocess
import tempfile


def _call_deepseek(model, messages, api_key, max_tokens=2000, temperature=0.7):
    """通过 curl 调用 DeepSeek API（绕过 Python TLS 指纹问题）"""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }, ensure_ascii=False)

    # Windows cmd 有长度限制，长 body 用临时文件传
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", encoding="utf-8", delete=False
    ) as f:
        f.write(payload)
        tmp_path = f.name

    try:
        cmd = [
            "curl", "-s", "--connect-timeout", "10", "--max-time", "120",
            "https://api.deepseek.com/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {api_key}",
            "-d", f"@{tmp_path}"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=130)
        if result.returncode != 0:
            raise Exception(f"curl 调用失败: {result.stderr}")

        data = json.loads(result.stdout)
        if "error" in data:
            raise Exception(f"API 错误: {data['error']}")
        return data["choices"][0]["message"]["content"]
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


class AIAssistant:
    def __init__(self, api_key=None):
        """初始化 AI 助手"""
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("未设置 DEEPSEEK_API_KEY")
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    def ask(self, question, context_notes):
        """基于笔记内容回答问题"""
        context = self._build_context(context_notes)

        system_prompt = """你是一个学习助手，帮助用户理解和回答关于他们笔记的问题。

请基于提供的笔记内容回答用户的问题。如果笔记中没有相关信息，请诚实地告诉用户。

回答要求：
- 简洁明了，直接回答问题
- 如果笔记中有相关信息，优先引用笔记内容
- 可以适当补充相关知识，但要标注这是补充内容
- 使用友好、温暖的语气"""

        user_message = f"""用户问题：{question}

相关笔记：
{context}

请基于以上笔记内容回答用户的问题。"""

        try:
            return _call_deepseek(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                api_key=self.api_key,
                max_tokens=2000,
                temperature=0.7
            )
        except Exception as e:
            raise Exception(f"AI 调用失败: {str(e)}")

    def _build_context(self, notes):
        """构建笔记上下文"""
        if not notes:
            return "（没有找到相关笔记）"

        context_parts = []
        for i, note in enumerate(notes, 1):
            title = note.get('title', '无标题')
            content = note.get('content', '')
            timestamp = note.get('timestamp', '')

            context_parts.append(f"""
【笔记 {i}】
标题：{title}
时间：{timestamp}
内容：
{content}
""")

        return "\n".join(context_parts)
