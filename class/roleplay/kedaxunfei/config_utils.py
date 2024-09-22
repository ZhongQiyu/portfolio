# pdf_extractor.py

import fitz  # PyMuPDF
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import requests
import time
import hashlib
import base64
import json
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
import argparse

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
    def __init__(self, text, knowledge_patterns):
        self.text = text
        self.knowledge_patterns = knowledge_patterns
        self.knowledge_points = []

    def extract_knowledge_points(self):
        for pattern in self.knowledge_patterns:
            matches = re.findall(pattern['regex'], self.text)
            for match in matches:
                parent = pattern['parent']
                child = match if pattern['child'] is None else pattern['child']
                self.knowledge_points.append((parent, child))

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
        plt.title("知识图谱", fontproperties=font)
        plt.show()

# Replace these with your own values
APPID = 'ccb83ac9'  # 替换为你的AppID
API_KEY = '14362ac45a6c18985ee0731c06235cb0'  # 替换为你的API Key
API_SECRET = 'ZGM1MzIzZmIwNTAwYzM4Y2Y1MjlkZGY3'  # 替换为你的API Secret
AUDIO_FILE = 'path_to_your_audio_file.wav'  # 替换为你的音频文件路径

# 星火认知大模型Spark Max的URL值
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'

# 星火认知大模型调用秘钥信息
SPARKAI_APP_ID = 'ccb83ac9'
SPARKAI_API_SECRET = 'ZGM1MzIzZmIwNTAwYzM4Y2Y1MjlkZGY3'
SPARKAI_API_KEY = '14362ac45a6c18985ee0731c06235cb0'

# 星火认知大模型Spark Max的domain值
SPARKAI_DOMAIN = 'generalv3.5'

# 获取时间戳
def get_timestamp():
    return str(int(time.time()))

# 生成签名
def get_signature(api_key, api_secret, timestamp):
    signature = api_key + timestamp + api_secret
    hash = hashlib.md5()
    hash.update(signature.encode('utf-8'))
    return hash.hexdigest()

# 获取鉴权参数
def get_auth_params(api_key, api_secret):
    timestamp = get_timestamp()
    signature = get_signature(api_key, api_secret, timestamp)
    params = {
        'appid': APPID,
        'timestamp': timestamp,
        'sign': signature,
    }
    return params

# 读取音频文件
def read_audio(file_path):
    with open(file_path, 'rb') as f:
        audio_data = f.read()
    return audio_data

# 发送请求
def send_request(url, headers, data):
    response = requests.post(url, headers=headers, data=data)
    return response.json()

# 调用讯飞ASR服务
def call_asr():
    url = "http://api.xfyun.cn/v1/service/v1/iat"
    audio_data = read_audio(AUDIO_FILE)
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    params = get_auth_params(API_KEY, API_SECRET)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'X-Appid': APPID,
        'X-CurTime': params['timestamp'],
        'X-Param': base64.b64encode(json.dumps({
            'engine_type': 'sms16k',
            'aue': 'raw'
        }).encode('utf-8')).decode('utf-8'),
        'X-CheckSum': params['sign'],
    }
    data = {
        'audio': audio_base64
    }

    response = send_request(url, headers, data)
    print("ASR Response:", response)
    return response

# 调用讯飞Spark大语言模型
def call_llm(user_input):
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content=user_input
    )]
    handler = ChunkPrintHandler()
    response = spark.generate([messages], callbacks=[handler])
    print("LLM Response:", response)
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='从PDF文件提取文本、调用ASR和LLM服务，并构建知识图谱')
    parser.add_argument('pdf_files', nargs='+', help='PDF文件路径列表')
    parser.add_argument('--audio', required=True, help='音频文件路径')
    args = parser.parse_args()

    # 设置音频文件路径
    AUDIO_FILE = args.audio

    # 创建PDFTextExtractor实例并提取文本
    extractor = PDFTextExtractor(args.pdf_files)
    extractor.extract_text_from_pdfs()
    cleaned_text = extractor.get_cleaned_text()

    # 打印部分清理后的文本内容以供检查
    print(cleaned_text[:2000])  # 这里只打印前2000个字符以供检查

    # 定义知识点模式
    knowledge_patterns = [
        {'regex': r'贝叶斯决策理论', 'parent': '模式识别', 'child': '贝叶斯决策理论'},
        {'regex': r'贝叶斯公式', 'parent': '贝叶斯决策理论', 'child': '贝叶斯公式'},
        {'regex': r'先验概率', 'parent': '贝叶斯决策理论', 'child': '先验概率'},
        {'regex': r'后验概率', 'parent': '贝叶斯决策理论', 'child': '后验概率'},
        {'regex': r'最大后验估计', 'parent': '贝叶斯决策理论', 'child': '最大后验估计'},
        {'regex': r'最小错误率决策', 'parent': '贝叶斯决策理论', 'child': '最小错误率决策'},
        {'regex': r'最小风险决策', 'parent': '贝叶斯决策理论', 'child': '最小风险决策'},
        {'regex': r'概率密度函数估计', 'parent': '模式识别', 'child': '概率密度函数估计'},
        {'regex': r'参数估计', 'parent': '概率密度函数估计', 'child': '参数估计'},
        {'regex': r'矩估计', 'parent': '参数估计', 'child': '矩估计'},
        {'regex': r'最大似然估计', 'parent': '参数估计', 'child': '最大似然估计'},
        {'regex': r'贝叶斯估计', 'parent': '参数估计', 'child': '贝叶斯估计'},
        {'regex': r'非参数估计', 'parent': '概率密度函数估计', 'child': '非参数估计'},
        {'regex': r'Parzen窗法', 'parent': '非参数估计', 'child': 'Parzen窗法'},
        {'regex': r'k-近邻法', 'parent': '非参数估计', 'child': 'k-近邻法'},
        {'regex': r'特征选择和变换', 'parent': '模式识别', 'child': '特征选择和变换'},
        {'regex': r'特征提取', 'parent': '特征选择和变换', 'child': '特征提取'},
        {'regex': r'降维', 'parent': '特征提取', 'child': '降维'},
        {'regex': r'特征选择', 'parent': '特征选择和变换', 'child': '特征选择'},
        {'regex': r'维数灾难', 'parent': '特征选择', 'child': '维数灾难'},
        {'regex': r'聚类分析', 'parent': '模式识别', 'child': '聚类分析'},
        {'regex': r'K-均值算法', 'parent': '聚类分析', 'child': 'K-均值算法'},
        {'regex': r'层次聚类', 'parent': '聚类分析', 'child': '层次聚类'},
        {'regex': r'相似性测度', 'parent': '聚类分析', 'child': '相似性测度'}
    ]

    # 创建KnowledgeGraphBuilder实例并构建知识图谱
    kg_builder = KnowledgeGraphBuilder(cleaned_text, knowledge_patterns)
    kg_builder.extract_knowledge_points()
    G = kg_builder.build_graph()
    kg_builder.draw_graph(G)

    # 调用ASR
    asr_result = call_asr()

    # 假设ASR结果中包含识别到的文本内容
    if 'data' in asr_result and 'result' in asr_result['data']:
        recognized_text = asr_result['data']['result']
        print("Recognized Text:", recognized_text)

        # 调用LLM
        llm_result = call_llm(recognized_text)
        print("LLM Result:", llm_result)
    else:
        print("ASR failed to recognize text.")
