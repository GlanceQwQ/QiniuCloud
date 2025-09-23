import asyncio
import requests
import json

async def test_ai_service():
    """测试AI服务是否正常工作"""
    base_url = "http://localhost:8000"
    
    # 测试数据
    test_data = {
        "guest_name": "测试用户",
        "character_id": "sarahmoon001",  # Sarah Moon
        "content": "你好，今天天气怎么样？"
    }
    
    try:
        # 1. 创建会话
        print("1. 创建会话...")
        conversation_response = requests.post(
            f"{base_url}/api/messages/conversations",
            json={
                "character_id": test_data["character_id"],
                "session_prompt": ""
            }
        )
        
        if conversation_response.status_code != 200:
            print(f"创建会话失败: {conversation_response.status_code} - {conversation_response.text}")
            return False
            
        conversation_data = conversation_response.json()
        conversation_id = conversation_data["id"]
        print(f"会话创建成功，ID: {conversation_id}")
        
        # 2. 发送消息
        print("2. 发送测试消息...")
        message_response = requests.post(
            f"{base_url}/api/messages/conversations/{conversation_id}/messages",
            json={
                "content": test_data["content"]
            },
            stream=True
        )
        
        if message_response.status_code != 200:
            print(f"发送消息失败: {message_response.status_code} - {message_response.text}")
            return False
            
        print("AI回复:")
        full_response = ""
        for line in message_response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data = line_text[6:]  # 移除 'data: ' 前缀
                    if data.strip() and data != '[DONE]':
                        try:
                            chunk_data = json.loads(data)
                            if 'content' in chunk_data:
                                content = chunk_data['content']
                                print(content, end='', flush=True)
                                full_response += content
                        except json.JSONDecodeError:
                            continue
        
        print("\n")
        
        if full_response:
            print("✅ AI服务测试成功！")
            print(f"完整回复: {full_response[:100]}...")
            return True
        else:
            print("❌ AI服务测试失败：没有收到回复")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试AI服务...")
    result = asyncio.run(test_ai_service())
    if result:
        print("\n🎉 所有测试通过！AI服务正常工作。")
    else:
        print("\n⚠️ 测试失败，请检查服务配置。")