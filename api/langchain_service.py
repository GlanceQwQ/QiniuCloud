from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import List, Dict, AsyncGenerator, Optional
import asyncio
import re
from config import settings

class LangChainAIService:
    def __init__(self):
        self.llm = None
        self.memory_store = {}  # 存储每个会话的记忆
        self._init_llm()
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        if not text:
            return "en"
        
        # 检测中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        chinese_chars = len(chinese_pattern.findall(text))
        
        # 检测日文字符
        japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]')
        japanese_chars = len(japanese_pattern.findall(text))
        
        # 检测韩文字符
        korean_pattern = re.compile(r'[\uac00-\ud7af]')
        korean_chars = len(korean_pattern.findall(text))
        
        # 检测俄文字符
        russian_pattern = re.compile(r'[\u0400-\u04ff]')
        russian_chars = len(russian_pattern.findall(text))
        
        # 检测阿拉伯文字符
        arabic_pattern = re.compile(r'[\u0600-\u06ff]')
        arabic_chars = len(arabic_pattern.findall(text))
        
        total_chars = len(text)
        
        # 如果中文字符占比超过30%，认为是中文
        if chinese_chars / total_chars > 0.3:
            return "zh"
        # 如果日文字符占比超过20%，认为是日文
        elif japanese_chars / total_chars > 0.2:
            return "ja"
        # 如果韩文字符占比超过20%，认为是韩文
        elif korean_chars / total_chars > 0.2:
            return "ko"
        # 如果俄文字符占比超过20%，认为是俄文
        elif russian_chars / total_chars > 0.2:
            return "ru"
        # 如果阿拉伯文字符占比超过20%，认为是阿拉伯文
        elif arabic_chars / total_chars > 0.2:
            return "ar"
        # 默认为英文
        else:
            return "en"
    
    def get_language_instruction(self, language_code: str) -> str:
        """根据语言代码获取语言指令"""
        language_instructions = {
            "zh": "IMPORTANT: Always respond in Chinese (中文).",
            "en": "IMPORTANT: Always respond in English.",
            "ja": "IMPORTANT: Always respond in Japanese (日本語).",
            "ko": "IMPORTANT: Always respond in Korean (한국어).",
            "ru": "IMPORTANT: Always respond in Russian (Русский).",
            "ar": "IMPORTANT: Always respond in Arabic (العربية)."
        }
        return language_instructions.get(language_code, "IMPORTANT: Always respond in English.")
    
    def _init_llm(self):
        """初始化LangChain LLM"""
        if settings.ai_service_provider == "openrouter":
            self.llm = ChatOpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                model=settings.default_ai_model,
                temperature=0.7,
                streaming=True
            )
        elif settings.ai_service_provider == "openai":
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.default_ai_model,
                temperature=0.7,
                streaming=True
            )
    
    def get_memory(self, conversation_id: str) -> ConversationBufferMemory:
        """获取或创建会话记忆"""
        if conversation_id not in self.memory_store:
            self.memory_store[conversation_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        return self.memory_store[conversation_id]
    
    def create_prompt_template(self, system_prompt: str) -> ChatPromptTemplate:
        """创建提示词模板"""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    
    async def generate_response(
        self,
        conversation_id: str,
        user_input: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        if not self.llm:
            yield "AI服务暂不可用，请稍后重试。"
            return
        
        try:
            # 检测用户输入的语言
            detected_language = self.detect_language(user_input)
            language_instruction = self.get_language_instruction(detected_language)
            
            # 将语言指令添加到系统提示词中
            enhanced_system_prompt = f"{system_prompt}\n\n{language_instruction}"
            
            memory = self.get_memory(conversation_id)
            prompt_template = self.create_prompt_template(enhanced_system_prompt)
            
            # 构建完整提示词
            messages = prompt_template.format_messages(
                input=user_input,
                chat_history=memory.chat_memory.messages
            )
            
            # 流式生成响应
            response = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    response += chunk.content
                    yield chunk.content
            
            # 更新记忆
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(response)
            
        except Exception as e:
            yield f"抱歉，AI服务出现错误：{str(e)}"
    
    async def generate_summary(
        self,
        conversation_id: str,
        max_length: int = 100
    ) -> str:
        """生成会话摘要"""
        if not self.llm:
            return "会话摘要"
        
        try:
            memory = self.get_memory(conversation_id)
            messages = memory.chat_memory.messages
            
            if not messages:
                return "会话摘要"
            
            # 使用LangChain的摘要功能
            from langchain.chains.summarize import load_summarize_chain
            from langchain.docstore.document import Document
            
            # 将消息转换为文档
            text = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-10:]])
            docs = [Document(page_content=text)]
            
            # 生成摘要
            chain = load_summarize_chain(self.llm, chain_type="stuff")
            summary = await chain.arun(docs)
            
            return summary[:max_length] if summary else "会话摘要"
            
        except Exception as e:
            return "会话摘要"
    
    def build_conversation_context(
        self,
        messages: List[Dict],
        system_prompt: str,
        max_context_length: int = 4000
    ) -> List[Dict]:
        """构建对话上下文（保持与原API兼容）"""
        context = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息
        for message in messages[-10:]:  # 限制最近10条消息
            context.append({
                "role": "user" if message.get("role") == "user" else "assistant",
                "content": message.get("content", "")
            })
        
        return context

# 全局服务实例
langchain_ai_service = LangChainAIService()