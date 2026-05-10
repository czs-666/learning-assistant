# 学习助手

个人知识库管理系统，支持笔记管理、文件上传和智能搜索。

## 功能特性

### 📝 笔记管理
- **手动添加笔记**：支持文本输入，保存时可选择添加标题
- **文件上传**：支持 PDF、Word (.docx)、TXT、Markdown 格式
- **自动提取**：上传文件后自动提取文本内容并保存

### 🔍 搜索功能
- **关键词搜索**：按标题或内容搜索笔记
- **高亮显示**：搜索结果中关键词自动高亮
- **折叠展示**：笔记默认折叠，点击展开查看详情

### ✏️ 编辑功能
- **内联编辑**：直接在笔记列表中编辑
- **标题修改**：可修改笔记标题和内容
- **实时保存**：编辑后立即保存到数据库

### 💾 数据存储
- **SQLite 数据库**：轻量级本地数据库
- **文件管理**：上传的文件保存在 `data/uploads/` 目录
- **数据持久化**：所有笔记和文件永久保存

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML + JavaScript
- **数据库**：SQLite
- **文件处理**：PyPDF2、python-docx

## 本地运行

### 环境要求
- Python 3.11+
- pip

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/czs-666/learning-assistant.git
cd learning-assistant
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python app.py
```

4. 访问应用
打开浏览器访问：http://localhost:5000

## 部署到 Railway

1. Fork 本项目到你的 GitHub
2. 访问 [Railway](https://railway.app/)
3. 使用 GitHub 账号登录
4. 选择 "Deploy from GitHub repo"
5. 选择你 fork 的仓库
6. 等待自动部署完成
7. 在 Settings → Domains 获取访问链接

## 项目结构

```
learning-assistant/
├── app.py                 # Flask 应用主文件
├── database.py            # SQLite 数据库操作
├── file_handler.py        # 文件处理（PDF、Word 等）
├── requirements.txt       # Python 依赖
├── Procfile              # Railway 部署配置
├── runtime.txt           # Python 版本
├── railway.json          # Railway 构建配置
├── templates/
│   └── index.html        # 前端页面
└── data/
    ├── notes.db          # SQLite 数据库文件
    └── uploads/          # 上传文件存储目录
```

## 使用说明

### 添加笔记
1. 在"笔记"页面，选择"上传文件"或"手动输入"
2. 点击"保存笔记"
3. 弹窗中输入标题（可选）
4. 确认保存

### 搜索笔记
1. 切换到"搜索"标签
2. 输入关键词
3. 点击"搜索"或按回车
4. 查看搜索结果，关键词会高亮显示

### 编辑笔记
1. 在笔记列表中点击"编辑"按钮
2. 修改标题和内容
3. 点击"保存"

## 开源协议

MIT License

## 作者

czs-666

---

**记录知识，快速搜索** 📚
