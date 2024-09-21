# run_gradio.py

# 导入gradio、random、time库，他们的功能大致如名字所示
import gradio as gr # 通过as指定gradio库的别名为gr
import random
import time

# 自定义函数，功能是随机选返回指定语句，并与用户输入的 chat_query 一起组织为聊天记录的格式返回
def chat(chat_query, chat_history):
        # 在How are you 等语句里随机挑一个返回，放到 bot_message 变量里
        bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
        # 添加到 chat_history 变量里
        chat_history.append((chat_query, bot_message))
        # 返回 空字符，chat_history 变量，空字符用于清空 chat_query 组件，chat_history 用于更新 chatbot组件
        return "", chat_history

# gr.Blocks()：布局组件，创建并给了他一个名字叫 demo
with gr.Blocks() as demo:
    # gr.Chatbot()：输入输出组件，用于展示对话效果
    chatbot = gr.Chatbot([], elem_id="chat-box", label="聊天历史")
    # gr.Textbox()：输入输出组件，用于展示文字
    chat_query = gr.Textbox(label="输入问题", placeholder="输入需要咨询的问题")
    # gr.Button：控制组件，用于点击，可绑定不同的函数触发处理
    llm_submit_tab = gr.Button("发送", visible=True)
    
    # gr.Examples(): 输入输出组件，用于展示组件的样例，点击即可将内容输入给 chat_query 组件
    gr.Examples(["请介绍一下Datawhale。", "如何在大模型应用比赛中突围并获奖？", "请介绍一下基于Gradio的应用开发"], chat_query)

    # 定义gr.Textbox()文字组件 chat_query 的 submit 动作(回车提交)效果，执行函数为 chat, 第一个[chat_query, chatbot]是输入，第二个 [chat_query, chatbot] 是输出
    chat_query.submit(fn=chat, inputs=[chat_query, chatbot], outputs=[chat_query, chatbot])
    # 定义gr.Button()控制组件 llm_submit_tab 的 点击动作 效果，执行函数为 chat, 第一个[chat_query, chatbot]是输入，第二个 [chat_query, chatbot] 是输出，效果与上一行代码同
    llm_submit_tab.click(fn=chat, inputs=[chat_query, chatbot], outputs=[chat_query, chatbot])

# 运行demo
if __name__ == '__main__':
    demo.queue().launch()

# run_gradio.py

# SDK引入模型
from dwspark.models import ChatModel, Text2Img, ImageUnderstanding, Text2Audio, Audio2Text, EmbeddingModel
# 讯飞消息对象
from sparkai.core.messages import ChatMessage
# 日志
from loguru import logger
'''
对话
'''
# 模拟问题
question = '你好呀'
logger.info('----------批式调用对话----------')
model = ChatModel(config, stream=False)
logger.info(model.generate([ChatMessage(role="user", content=question)]))
logger.info('----------流式调用对话----------')
model = ChatModel(config, stream=True)
[ logger.info(r) for r in model.generate_stream(question)]
logger.info('done.')
'''
文字生成语音
'''
text = '2023年5月，讯飞星火大模型正式发布，迅速成为千万用户获取知识、学习知识的“超级助手”，成为解放生产力、释放想象力的“超级杠杆”。2024年4月，讯飞星火V3.5春季升级长文本、长图文、长语音三大能力。一年时间内，讯飞星火从1.0到3.5，每一次迭代都是里程碑式飞跃。'
audio_path = './demo.mp3'
t2a = Text2Audio(config)
# 对生成上锁，预防公有变量出现事务问题，但会降低程序并发性能。
t2a.gen_audio(text, audio_path)
'''
语音识别文字
'''
a2t = Audio2Text(config)
# 对生成上锁，预防公有变量出现事务问题，但会降低程序并发性能。
audio_text = a2t.gen_text(audio_path)
logger.info(audio_text)
'''
生成图片
'''
logger.info('----------生成图片----------')
prompt = '一只鲸鱼在快乐游泳的卡通头像'
t2i = Text2Img(config)
t2i.gen_image(prompt, './demo.jpg')
'''
图片解释
'''
logger.info('----------图片解释----------')
prompt = '请理解一下图片'
iu = ImageUnderstanding(config)
logger.info(iu.understanding(prompt, './demo.jpg'))
'''
获取文本向量
'''
logger.info('----------获取文本向量----------')
em = EmbeddingModel(config)
vector = em.get_embedding("我们是datawhale")
logger.info(vector)

**  

# chat_model.py

from typing import List, Iterable
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage
from dwspark.config import Config
from loguru import logger

class ChatModel:
    def __init__(self, config: Config, domain: str = 'generalv3.5', model_url: str = 'wss://spark-api.xf-yun.com/v3.5/chat', stream: bool = False):
        '''
        初始化模型
        :param config: 项目配置文件
        :param domain: 调用模型
        :param llm_url: 模型地址
        :param stream: 是否启用流式调用
        '''
        self.spark = ChatSparkLLM(
            spark_api_url=model_url,
            spark_app_id=config.XF_APPID,
            spark_api_key=config.XF_APIKEY,
            spark_api_secret=config.XF_APISECRET,
            spark_llm_domain=domain,
            streaming=stream,
        )
        self.stream = stream

    def generate(self, msgs: str | List[ChatMessage]) -> str:
        '''
        批式调用
        :param msgs: 发送消息，接收字符串或列表形式的消息
        :return:
        '''
        if self.stream:
            raise Exception('模型初始化为流式输出，请调用generate_stream方法')

        messages = self.__trans_msgs(msgs)
        resp = self.spark.generate([messages])
        return resp.generations[0][0].text

    def generate_stream(self, msgs: str | List[ChatMessage]) -> Iterable[str]:
        '''
        流式调用
        :param msgs: 发送消息，接收字符串或列表形式的消息
        :return:
        '''
        if not self.stream:
            raise Exception('模型初始化为批式输出，请调用generate方法')
        messages = self.__trans_msgs(msgs)
        resp_iterable = self.spark.stream(messages)
        for resp in resp_iterable:
            yield resp.content

    def __trans_msgs(self, msg: str):
        '''
        内部方法，将字符串转换为消息
        :param msgs: 字符串
        :return:
        '''
        if isinstance(msg, str):
            messages = [ChatMessage(role="user", content=msg)]
        else:
            messages = msg
        return messages
