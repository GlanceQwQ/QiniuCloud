import asyncio
import json
from typing import List, Dict, AsyncGenerator, Optional
from openai import AsyncOpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化AI客户端"""
        if settings.ai_service_provider == "openrouter" and settings.openrouter_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        elif settings.ai_service_provider == "openai" and settings.openai_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key
            )
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        if settings.ai_service_provider == "openrouter":
            return self.client is not None and settings.openrouter_api_key is not None
        elif settings.ai_service_provider == "openai":
            return self.client is not None and settings.openai_api_key is not None
        return False
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        if not self.is_available():
            yield "AI服务暂不可用，请稍后重试。"
            return
        
        try:
            model = model or settings.default_ai_model
            
            # 调用OpenAI API
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"AI服务调用失败: {e}")
            yield "抱歉，AI服务出现错误，请稍后重试。"
    
    async def generate_summary(
        self,
        messages: List[Dict[str, str]],
        max_length: int = 100
    ) -> str:
        """生成会话摘要"""
        if not self.is_available():
            return "会话摘要"
        
        try:
            # 构建摘要提示
            summary_messages = [
                {
                    "role": "system",
                    "content": f"请为以下对话生成一个简洁的摘要，不超过{max_length}个字符。只返回摘要内容，不要其他说明。"
                },
                {
                    "role": "user",
                    "content": "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[-10:]])
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=settings.default_ai_model,
                messages=summary_messages,
                temperature=0.3,
                max_tokens=50
            )
            
            summary = response.choices[0].message.content.strip()
            return summary[:max_length] if summary else "会话摘要"
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return "会话摘要"
    
    def build_conversation_context(
        self,
        character_system_prompt: str,
        character_greeting: str,
        session_prompt: Optional[str],
        message_history: List[Dict[str, str]],
        max_context_length: int = 4000
    ) -> List[Dict[str, str]]:
        """构建对话上下文"""
        messages = []
        
        # 1. 系统提示词
        system_content = character_system_prompt
        if session_prompt:
            system_content += f"\n\n会话设定：{session_prompt}"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # 2. 角色开场白（如果没有历史消息）
        if not message_history:
            messages.append({
                "role": "assistant",
                "content": character_greeting
            })
        else:
            # 3. 历史消息（保留最近的消息）
            total_length = len(system_content)
            selected_messages = []
            
            # 从最新消息开始，逐步添加到上下文中
            for msg in reversed(message_history):
                msg_length = len(msg["content"])
                if total_length + msg_length > max_context_length:
                    break
                
                selected_messages.insert(0, msg)
                total_length += msg_length
            
            messages.extend(selected_messages)
        
        return messages

# 全局AI服务实例
ai_service = AIService()