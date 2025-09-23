import requests
import json

def test_language_detection():
    base_url = "http://localhost:8000"
    
    # 登录获取token
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print("登录失败")
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取角色列表
    response = requests.get(f"{base_url}/api/characters/", headers=headers)
    if response.status_code != 200:
        print("获取角色失败")
        return
    
    result = response.json()
    characters = result.get('characters', [])
    print(f"获取到角色数量: {len(characters)}")
    
    if not characters:
        print("没有可用角色")
        return
    
    character_id = characters[0]['id']
    print(f"使用角色: {characters[0]['name']}")
    
    # 创建对话
    conversation_data = {
        "character_id": character_id,
        "session_prompt": "测试多语言对话功能"
    }
    
    response = requests.post(
        f"{base_url}/api/messages/conversations",
        json=conversation_data,
        headers=headers
    )
    if response.status_code != 200:
        print(f"创建对话失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return
    
    conversation_id = response.json()['id']
    print(f"创建对话成功: {conversation_id}")
    
    # 测试不同语言的消息
    test_messages = [
        {"content": "你好，请用中文回答我", "expected_lang": "中文"},
        {"content": "Hello, please respond in English", "expected_lang": "英文"},
        {"content": "こんにちは、日本語で答えてください", "expected_lang": "日文"},
        {"content": "안녕하세요, 한국어로 대답해주세요", "expected_lang": "韩文"}
    ]
    
    for i, test_msg in enumerate(test_messages, 1):
        print(f"\n=== 测试 {i}: {test_msg['expected_lang']} ===")
        print(f"用户输入: {test_msg['content']}")
        
        message_data = {
            "content": test_msg['content']
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/messages/conversations/{conversation_id}/messages",
                json=message_data,
                headers=headers,
                stream=True
            )
            
            if response.status_code == 200:
                print("AI回复: ", end="")
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'content' in data:
                                    content = data['content']
                                    print(content, end="", flush=True)
                                    full_response += content
                            except json.JSONDecodeError:
                                continue
                print()  # 换行
                print(f"完整回复: {full_response}")
            else:
                print(f"发送消息失败: {response.status_code}")
                print(f"错误信息: {response.text}")
        except Exception as e:
            print(f"请求异常: {e}")

if __name__ == "__main__":
    test_language_detection()