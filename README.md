# 学习助手

个人知识库问答系统，帮你记录和查询学习笔记。

## 快速启动

双击 `启动.bat` 文件，然后在浏览器访问 `http://localhost:5000`

## 功能

- **添加笔记**：粘贴学习内容，一键保存
- **智能问答**：输入问题，基于你的笔记回答
- **来源追溯**：显示答案来自哪些笔记

## 配置

需要设置 Claude API Key：

```bash
set ANTHROPIC_API_KEY=your_api_key_here
```

## 数据存储

笔记保存在 `data/notes.json`
