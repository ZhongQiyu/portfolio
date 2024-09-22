# extract.py

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def clean_text(text):
    # 替换连续的多个换行符和空格为一个空格
    text = ' '.join(text.split())
    return text

# 定义PDF文件路径
pdf_files = [
    "/mnt/data/pattern recognition_第一章.pdf",
    "/mnt/data/pattern recognition_第二章贝叶斯_2023.pdf",
    "/mnt/data/pattern recognition_第三章概率密度函数的估计2023.pdf",
    "/mnt/data/pattern recognition_第四章_判别阈代数方程法.pdf",
    "/mnt/data/pattern recognition_第五章_特征选择和特征变换（华侨大学）2023.pdf",
    "/mnt/data/pattern recognition_第五章PCA人脸识别算法及LDA算法分析.pdf",
    "/mnt/data/pattern recognition_第六章 聚类分析（华侨大学）.pdf"
]

# 提取并清理所有PDF文件的文本内容
all_text = ""
for pdf_file in pdf_files:
    text = extract_text_from_pdf(pdf_file)
    cleaned_text = clean_text(text)
    all_text += cleaned_text + "\n"

# 打印部分清理后的文本内容以供检查
print(all_text[:2000])  # 这里只打印前2000个字符以供检查
