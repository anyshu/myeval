#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连通性测试脚本
"""

import requests
import json

def test_api():
    """测试API连通性"""
    base_url = "http://127.0.0.1:18000/v1"
    api_key = "empty"
    model = "/data/models/fazhi/DeepSeek-V3-0324-HF-FP4/"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 测试消息
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "你好，请回答：1+1等于多少？只回答数字。"}
        ],
        "temperature": 0.0,
        "max_tokens": 10
    }
    
    try:
        print("正在测试API连通性...")
        print(f"API地址: {base_url}")
        print(f"模型: {model}")
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"✅ API连接成功！")
            print(f"模型回答: {answer}")
            return True
        else:
            print(f"❌ API请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    test_api() 