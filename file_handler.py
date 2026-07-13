#!/usr/bin/env python3
"""
文件处理模块 - 提取各种文档格式的文本内容
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from pypdf import PdfReader
from docx import Document


class FileHandler:
    """文件处理类"""

    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md'}

    @staticmethod
    def is_supported(filename: str) -> bool:
        """检查文件是否支持"""
        ext = Path(filename).suffix.lower()
        return ext in FileHandler.SUPPORTED_EXTENSIONS

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """从 PDF 文件提取文本"""
        try:
            text_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            return '\n\n'.join(text_content).strip()
        except Exception as e:
            raise Exception(f"PDF 文件解析失败: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """从 Word 文档提取文本"""
        try:
            doc = Document(file_path)
            text_content = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)

            return '\n\n'.join(text_content).strip()
        except Exception as e:
            raise Exception(f"Word 文档解析失败: {str(e)}")

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """从文本文件提取内容"""
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read().strip()
                except UnicodeDecodeError:
                    continue

            raise Exception("无法识别文件编码")
        except Exception as e:
            raise Exception(f"文本文件读取失败: {str(e)}")

    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, str]:
        """
        提取文件文本内容
        返回: (文本内容, 文件类型)
        """
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            text = FileHandler.extract_text_from_pdf(file_path)
            file_type = 'PDF'
        elif ext in ['.docx', '.doc']:
            text = FileHandler.extract_text_from_docx(file_path)
            file_type = 'Word'
        elif ext in ['.txt', '.md']:
            text = FileHandler.extract_text_from_txt(file_path)
            file_type = 'Text' if ext == '.txt' else 'Markdown'
        else:
            raise Exception(f"不支持的文件格式: {ext}")

        if not text:
            raise Exception("文件内容为空")

        return text, file_type
