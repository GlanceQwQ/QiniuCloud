import asyncio
import aiohttp
import json

async def test_qwen_model():
    """测试Qwen模型是否正常工作"""
    
    try:
        async with aiohttp.ClientSession() as session:
            print("正在测试Qwen模型...")
            
            # 第一步：创建会话
            print("1. 创建会话...")
            create_conversation_url = "http://localhost:8000/api/messages/conversations"
            conversation_data = {
                 "character_id": "40f1054554044b81"  # 小雪角色
             }
            
            async with session.post(create_conversation_url, json=conversation_data) as response:
                if response.status == 200:
                    conversation_response = await response.json()
                    conversation_id = conversation_response['id']
                    print(f"✅ 会话创建成功: {conversation_id}")
                else:
                    print(f"❌ 创建会话失败，状态码: {response.status}")
                    error_text = await response.text()
                    print(f"错误信息: {error_text}")
                    return
            
            # 第二步：发送消息
            print("\n2. 发送测试消息...")
            send_message_url = f"http://localhost:8000/api/messages/conversations/{conversation_id}/messages"
            message_data = {
                "content": "你好，请用中文介绍一下你自己"
            }
            
            print(f"发送消息: {message_data['content']}")
            
            async with session.post(send_message_url, json=message_data) as response:
                if response.status == 200:
                    print("\n=== Qwen模型响应 ===")
                    async for line in response.content:
                        if line:
                            try:
                                # 解析SSE数据
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data_str = line_str[6:]  # 移除'data: '前缀
                                    if data_str != '[DONE]':
                                        data = json.loads(data_str)
                                        if data.get('type') == 'content' and 'content' in data:
                                            print(data['content'], end='', flush=True)
                            except json.JSONDecodeError:
                                continue
                    print("\n\n=== 测试完成 ===")
                    print("✅ Qwen模型工作正常！")
                else:
                    print(f"❌ 发送消息失败，状态码: {response.status}")
                    error_text = await response.text()
                    print(f"错误信息: {error_text}")
                    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_qwen_model())