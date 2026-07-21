# 学习助手

个人知识库 RAG 问答系统。上传文档/手动输入 → 自动提取存储 → 关键词搜索 → AI 基于你的笔记智能回答。

**技术栈**：Python · Flask · SQLite · DeepSeek API · 原生 JS（无框架）

## 功能

| 模块 | 说明 |
|------|------|
| 笔记管理 | 手动输入 / 文件上传（PDF、Word、TXT、Markdown），内联编辑删除 |
| 关键词搜索 | 全文检索，命中关键词金色高亮，结果折叠展开 |
| AI 问答 | 基于 DeepSeek API，提取笔记作为上下文，RAG 式回答 |
| 文件解析 | PDF 提取（PyPDF2）、Word 提取（python-docx）、多编码兼容 |

## 快速开始

```bash
git clone https://github.com/czs-666/learning-assistant.git
cd learning-assistant
pip install -r requirements.txt
```

在项目根目录创建 `.env`，填入 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-your-key-here
```

启动：

```bash
python app.py
```

浏览器打开 `http://localhost:5000`

## 项目结构

```
├── app.py             # Flask 应用入口，路由定义
├── database.py        # SQLite 数据层，含中文分词搜索
├── ai_assistant.py    # DeepSeek API 调用，RAG 上下文构建
├── file_handler.py    # PDF/Word/TXT/Markdown 文本提取
├── templates/
│   └── index.html     # 前端界面（原生 JS SPA）
└── data/              # 运行时数据（SQLite + 上传文件）
```

## 设计

- AI-native 开发：全程使用 Claude Code 辅助编码
- 无前端框架依赖，单 HTML 文件完成 SPA 交互
- SQLite 零配置，启动即用
- 金色 + 大留白 + 思源宋体，克制高级感
