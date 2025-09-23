import asyncio
import sys
sys.path.append('.')

from langchain_service import langchain_ai_service

async def test_free_model():
    """测试免费AI模型功能"""
    print("开始测试免费AI模型...")
    
    # 测试中文对话
    print("\n=== 测试中文对话 ===")
    conversation_id = "test_free_model_zh"
    system_prompt = "你是一个友好的AI助手。"
    user_input = "你好，今天天气怎么样？"
    
    print(f"用户输入: {user_input}")
    print("AI回复: ", end="")
    
    response = ""
    async for chunk in langchain_ai_service.generate_response(
        conversation_id=conversation_id,
        user_input=user_input,
        system_prompt=system_prompt
    ):
        print(chunk, end="", flush=True)
        response += chunk
    
    print("\n")
    
    # 测试英文对话
    print("\n=== 测试英文对话 ===")
    conversation_id = "test_free_model_en"
    system_prompt = "You are a helpful AI assistant."
    user_input = "Hello, how are you today?"
    
    print(f"用户输入: {user_input}")
    print("AI回复: ", end="")
    
    response = ""
    async for chunk in langchain_ai_service.generate_response(
        conversation_id=conversation_id,
        user_input=user_input,
        system_prompt=system_prompt
    ):
        print(chunk, end="", flush=True)
        response += chunk
    
    print("\n")
    print("免费AI模型测试完成！")

if __name__ == "__main__":
    asyncio.run(test_free_model())