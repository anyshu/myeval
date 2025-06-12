#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连通性测试脚本
"""

import requests
import json
import re
from typing import Optional

def extract_answer_from_response(response: str) -> Optional[str]:
    """从模型响应中提取答案"""
    if not response:
        return None
        
    # 清理响应文本
    response = response.strip().upper()
    
    # 尝试不同的提取方法
    # 方法1：直接查找单个字母
    if response in ['A', 'B', 'C', 'D']:
        return response
    
    # 方法2：查找各种格式的答案模式
    patterns = [
        r'\\BOXED\{([ABCD])\}',  # \boxed{D} 格式
        r'答案是\s*([ABCD])',
        r'选择\s*([ABCD])',
        r'答案：\s*([ABCD])',
        r'选择：\s*([ABCD])',
        r'THE CORRECT ANSWER IS\s*([ABCD])',
        r'ANSWER:\s*([ABCD])',
        r'ANSWER IS\s*([ABCD])',
        r'^([ABCD])\.?$',  # 单独的字母，可能带点号
        r'^([ABCD])\s*[-:]',  # 字母后跟冒号或破折号
        r'^\s*([ABCD])\s*$',  # 前后可能有空格的单个字母
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            return match.group(1)
    
    # 方法3：查找最后一个出现的单独字母（通常是最终答案）
    letters_found = re.findall(r'\b([ABCD])\b', response)
    if letters_found:
        return letters_found[-1]
    
    # 方法4：查找第一个出现的A、B、C、D
    for char in response:
        if char in ['A', 'B', 'C', 'D']:
            return char
    
    return None

def test_api():
    """测试API连通性"""
    base_url = "http://127.0.0.1:18000/v1"
    api_key = "empty"
    model = "/data/models/fazhi/DeepSeek-V3-0324-HF-FP4/"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 测试消息 - 使用MMLU格式的问题
    test_question = """Find all zeros in the indicated finite field of the given polynomial with coefficients in that field. x^5 + 3x^3 + x^2 + 2x in Z_5

A. 0
B. 1
C. 0,1
D. 0,4

Please choose the correct answer. Only respond with the letter (A, B, C, or D), no explanation needed:"""
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": test_question}
        ],
        "temperature": 0.0,
        "max_tokens": 512
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
            raw_answer = result['choices'][0]['message']['content']
            print(f"✅ API连接成功！")
            print(f"模型原始回答: {raw_answer}")
            
            # 测试答案提取
            extracted = extract_answer_from_response(raw_answer)
            print(f"提取的答案: {extracted}")
            print(f"期望答案: D")
            
            if extracted == "D":
                print("✅ 答案提取成功！")
            else:
                print("⚠️ 答案提取可能有问题，请检查提取逻辑")
            
            return True
        else:
            print(f"❌ API请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    test_api() 