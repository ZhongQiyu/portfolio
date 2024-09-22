# main.py

import os
import fitz  # PyMuPDF
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

class PDFTextExtractor:
    def __init__(self, pdf_paths):
        self.pdf_paths = pdf_paths
        self.raw_text = ""
        self.cleaned_text = ""
    
    def extract_text_from_pdfs(self):
        for pdf_path in self.pdf_paths:
            self.raw_text += self.extract_text_from_pdf(pdf_path) + "\n"
        self.cleaned_text = self.clean_text(self.raw_text)
    
    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text")
        return text

    def clean_text(self, text):
        # 替换连续的多个换行符和空格为一个空格
        text = ' '.join(text.split())
        # 移除多余的空格和特殊字符
        text = re.sub(r'\s+', ' ', text)
        # 使用正则表达式来分割章节
        segments = re.split(r'华侨大学计算机学院', text)
        return '\n'.join(segments)

    def get_cleaned_text(self):
        return self.cleaned_text

class KnowledgeGraphBuilder:
    def __init__(self, text):
        self.text = text
        self.knowledge_points = []

    def extract_knowledge_points(self):
        text = self.text
        if "贝叶斯决策理论" in text:
            self.knowledge_points.append(("模式识别", "贝叶斯决策理论"))
            if "贝叶斯公式" in text:
                self.knowledge_points.append(("贝叶斯决策理论", "贝叶斯公式"))
            if "先验概率" in text:
                self.knowledge_points.append(("贝叶斯决策理论", "先验概率"))
            if "后验概率" in text:
                self.knowledge_points.append(("贝叶斯决策理论", "后验概率"))
            if "最大后验估计" in text:
                self.knowledge_points.append(("贝叶斯决策理论", "最大后验估计"))
            if "最小错误率决策" in text:
                self.knowledge_points.append(("贝叶斯决策理论", "最小错误率决策"))
            if "最小风险决策" in text:
                self.knowledge_points.append(("贝叶斯决策理论", "最小风险决策"))

        if "概率密度函数估计" in text:
            self.knowledge_points.append(("模式识别", "概率密度函数估计"))
            if "参数估计" in text:
                self.knowledge_points.append(("概率密度函数估计", "参数估计"))
                if "矩估计" in text:
                    self.knowledge_points.append(("参数估计", "矩估计"))
                if "最大似然估计" in text:
                    self.knowledge_points.append(("参数估计", "最大似然估计"))
                if "贝叶斯估计" in text:
                    self.knowledge_points.append(("参数估计", "贝叶斯估计"))
            if "非参数估计" in text:
                self.knowledge_points.append(("概率密度函数估计", "非参数估计"))
                if "Parzen窗法" in text:
                    self.knowledge_points.append(("非参数估计", "Parzen窗法"))
                if "k-近邻法" in text:
                    self.knowledge_points.append(("非参数估计", "k-近邻法"))

        if "特征选择和变换" in text:
            self.knowledge_points.append(("模式识别", "特征选择和变换"))
            if "特征提取" in text:
                self.knowledge_points.append(("特征选择和变换", "特征提取"))
                if "降维" in text:
                    self.knowledge_points.append(("特征提取", "降维"))
            if "特征选择" in text:
                self.knowledge_points.append(("特征选择和变换", "特征选择"))
                if "维数灾难" in text:
                    self.knowledge_points.append(("特征选择", "维数灾难"))

        if "聚类分析" in text:
            self.knowledge_points.append(("模式识别", "聚类分析"))
            if "K-均值算法" in text:
                self.knowledge_points.append(("聚类分析", "K-均值算法"))
            if "层次聚类" in text:
                self.knowledge_points.append(("聚类分析", "层次聚类"))
            if "相似性测度" in text:
                self.knowledge_points.append(("聚类分析", "相似性测度"))

    def build_graph(self):
        G = nx.DiGraph()
        for kp in self.knowledge_points:
            G.add_edge(kp[0], kp[1])
        return G

    def draw_graph(self, G):
        # 设置中文字体
        font = FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size=14)
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, edge_color='gray', linewidths=1, font_size=12, font_weight='bold', arrows=True, arrowstyle='-|>', arrowsize=20, font_family='sans-serif', fontproperties=font)
        plt.title("模式识别知识图谱", fontproperties=font)
        plt.show()

# 主程序
if __name__ == "__main__":
        # 定义PDF文件路径
    user_directory = "/Users/qaz1214/Downloads/"
    root_directory = os.path.join(user_directory, "course-diagram/data/模式识别课程ppt")
    pdf_files = [os.path.join(root_directory, pdf) for pdf in ["pattern recognition_第一章.pdf","pattern recognition_第二章贝叶斯_2023.pdf", "pattern recognition_第三章概率密度函数的估计2023.pdf",
                                                           "pattern recognition_第四章_判别阈代数方程法.pdf", "pattern recognition_第五章_特征选择和特征变换（华侨大学）2023.pdf",
                                                           "pattern recognition_第五章PCA人脸识别算法及LDA算法分析.pdf", "pattern recognition_第六章 聚类分析（华侨大学）.pdf"]]

    # 创建PDFTextExtractor实例并提取文本
    extractor = PDFTextExtractor(pdf_files)
    extractor.extract_text_from_pdfs()
    cleaned_text = extractor.get_cleaned_text()

    # 打印部分清理后的文本内容以供检查
    print(cleaned_text[:2000])  # 这里只打印前2000个字符以供检查

    # 创建KnowledgeGraphBuilder实例并构建知识图谱
    kg_builder = KnowledgeGraphBuilder(cleaned_text)
    kg_builder.extract_knowledge_points()
    G = kg_builder.build_graph()
    kg_builder.draw_graph(G)
