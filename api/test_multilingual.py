import asyncio
import aiohttp
import json

# 测试多语言对话功能
async def test_multilingual_chat():
    base_url = "http://localhost:8000"
    
    # 测试用户登录
    async with aiohttp.ClientSession() as session:
        # 1. 注册测试用户
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        try:
            async with session.post(f"{base_url}/api/auth/register", json=register_data) as resp:
                if resp.status == 200:
                    print("✓ 用户注册成功")
                else:
                    print(f"用户注册失败: {resp.status}")
        except:
            print("用户可能已存在，继续测试")
        
        # 2. 用户登录
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        async with session.post(f"{base_url}/api/auth/login", json=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result['access_token']
                print("✓ 用户登录成功")
            else:
                print(f"登录失败: {resp.status}")
                return
        
        # 设置认证头
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. 获取角色列表
        async with session.get(f"{base_url}/api/characters/", headers=headers) as resp:
            if resp.status == 200:
                characters = await resp.json()
                print(f"✓ 获取到 {len(characters['characters'])} 个角色")
                character_id = characters['characters'][0]['id']
                character_name = characters['characters'][0]['name']
                print(f"选择角色: {character_name} ({character_id})")
            else:
                print(f"获取角色失败: {resp.status}")
                return
        
        # 4. 创建对话
        conversation_data = {
            "character_id": character_id,
            "title": "多语言测试对话"
        }
        
        async with session.post(f"{base_url}/api/conversations", json=conversation_data, headers=headers) as resp:
            if resp.status == 200:
                conversation = await resp.json()
                conversation_id = conversation['id']
                print(f"✓ 创建对话成功: {conversation_id}")
            else:
                print(f"创建对话失败: {resp.status}")
                return
        
        # 5. 测试多语言对话
        test_messages = [
            {"text": "你好，很高兴认识你！", "language": "中文"},
            {"text": "Hello, nice to meet you!", "language": "英文"},
            {"text": "こんにちは、はじめまして！", "language": "日文"},
            {"text": "안녕하세요, 만나서 반갑습니다!", "language": "韩文"},
        ]
        
        for i, test_msg in enumerate(test_messages, 1):
            print(f"\n=== 测试 {i}: {test_msg['language']} ===")
            print(f"用户输入: {test_msg['text']}")
            
            message_data = {
                "content": test_msg['text']
            }
            
            async with session.post(
                f"{base_url}/api/conversations/{conversation_id}/messages", 
                json=message_data, 
                headers=headers
            ) as resp:
                if resp.status == 200:
                    print("AI回复: ", end="")
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line.decode().strip())
                                if 'content' in data:
                                    print(data['content'], end="")
                            except:
                                pass
                    print()  # 换行
                else:
                    print(f"发送消息失败: {resp.status}")
            
            # 等待一下再发送下一条消息
            await asyncio.sleep(1)
        
        print("\n=== 多语言对话测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_multilingual_chat())