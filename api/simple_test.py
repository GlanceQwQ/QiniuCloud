import requests
import json

def test_basic_api():
    base_url = "http://localhost:8000"
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/")
        print(f"根路径测试: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"根路径测试失败: {e}")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        print(f"健康检查: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")
    
    # 测试用户注册
    try:
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"用户注册: {response.status_code}")
        if response.status_code != 200:
            print(f"注册失败响应: {response.text}")
        else:
            print(f"注册成功: {response.json()}")
    except Exception as e:
        print(f"用户注册失败: {e}")
    
    # 测试用户登录
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"用户登录: {response.status_code}")
        if response.status_code != 200:
            print(f"登录失败响应: {response.text}")
        else:
            result = response.json()
            print(f"登录成功: {result}")
            return result.get('access_token')
    except Exception as e:
        print(f"用户登录失败: {e}")
    
    return None

if __name__ == "__main__":
    test_basic_api()