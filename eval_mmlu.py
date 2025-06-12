#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MMLU 评估程序
通过API调用模型进行多选题测试
"""

import os
import csv
import json
import time
import requests
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime
import statistics

class MMLUEvaluator:
    def __init__(self, base_url: str, api_key: str, model_name: str):
        """
        初始化MMLU评估器
        
        Args:
            base_url: API的基础URL
            api_key: API密钥
            model_name: 模型名称
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
    def call_api(self, messages: List[Dict], temperature: float = 0.0, max_tokens: int = 512) -> Optional[str]:
        """
        调用API获取模型响应
        
        Args:
            messages: 对话消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            模型的响应文本
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"API调用异常: {e}")
            return None
    
    def format_question(self, question: str, options: Dict[str, str]) -> str:
        """
        格式化问题为提示词
        
        Args:
            question: 问题文本
            options: 选项字典 {'A': '选项A', 'B': '选项B', ...}
            
        Returns:
            格式化后的问题字符串
        """
        formatted = f"{question}\n\n"
        for key in ['A', 'B', 'C', 'D']:
            if key in options:
                formatted += f"{key}. {options[key]}\n"
        
        formatted += "\nPlease choose the correct answer. Only respond with the letter (A, B, C, or D), no explanation needed:"
        return formatted
    
    def extract_answer(self, response: str) -> Optional[str]:
        """
        从模型响应中提取答案
        
        Args:
            response: 模型响应文本
            
        Returns:
            提取的答案字母 (A, B, C, D)
        """
        if not response:
            return None
            
        # 清理响应文本
        response = response.strip().upper()
        
        import re
        
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
    
    def evaluate_dataset(self, csv_file: str, sample_size: Optional[int] = None) -> Dict:
        """
        评估单个数据集文件
        
        Args:
            csv_file: CSV文件路径
            sample_size: 采样大小（None表示全部）
            
        Returns:
            评估结果字典
        """
        results = {
            'correct': 0,
            'total': 0,
            'accuracy': 0.0,
            'details': [],
            'errors': []
        }
        
        print(f"开始评估: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # 检查文件是否正确读取
                if not rows:
                    print(f"警告: 文件 {csv_file} 为空或无法读取")
                    return results
                
                # 检查列名
                fieldnames = reader.fieldnames
                print(f"检测到的列名: {fieldnames}")
                
                required_columns = ['input', 'A', 'B', 'C', 'D', 'target']
                missing_columns = [col for col in required_columns if col not in fieldnames]
                if missing_columns:
                    print(f"错误: 缺少必需的列: {missing_columns}")
                    return results
                
                # 采样
                if sample_size and sample_size < len(rows):
                    import random
                    rows = random.sample(rows, sample_size)
                
                for i, row in enumerate(rows):
                    # 添加调试信息
                    if i == 0:
                        print(f"第一行数据的键: {list(row.keys())}")
                    
                    try:
                        question = row['input']
                        options = {
                            'A': row['A'],
                            'B': row['B'], 
                            'C': row['C'],
                            'D': row['D']
                        }
                        correct_answer = row['target']
                    except KeyError as e:
                        print(f"键错误在第{i+1}行: {e}")
                        print(f"可用的键: {list(row.keys())}")
                        continue
                    
                    # 格式化问题
                    formatted_question = self.format_question(question, options)
                    
                    # 调用API
                    messages = [
                        {"role": "user", "content": formatted_question}
                    ]
                    
                    response = self.call_api(messages)
                    predicted_answer = self.extract_answer(response)
                    
                    # 记录结果
                    is_correct = predicted_answer == correct_answer
                    results['total'] += 1
                    if is_correct:
                        results['correct'] += 1
                    
                    detail = {
                        'question_id': i + 1,
                        'question': question,
                        'options': options,
                        'correct_answer': correct_answer,
                        'predicted_answer': predicted_answer,
                        'raw_response': response,
                        'is_correct': is_correct
                    }
                    results['details'].append(detail)
                    
                    if not is_correct:
                        results['errors'].append(detail)
                    
                    print(f"进度: {i+1}/{len(rows)} - 正确: {results['correct']}/{results['total']} ({results['correct']/results['total']*100:.1f}%)")
                    
                    # 添加延迟避免API限制
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"评估出错: {e}")
            return results
        
        # 计算准确率
        if results['total'] > 0:
            results['accuracy'] = results['correct'] / results['total']
        
        return results
    
    def save_results(self, results: Dict, output_file: str):
        """
        保存评估结果到文件
        
        Args:
            results: 评估结果
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
    
    def print_summary(self, results: Dict, dataset_name: str):
        """
        打印评估结果摘要
        
        Args:
            results: 评估结果
            dataset_name: 数据集名称
        """
        print(f"\n{'='*60}")
        print(f"数据集: {dataset_name}")
        print(f"总题数: {results['total']}")
        print(f"正确数: {results['correct']}")
        print(f"准确率: {results['accuracy']:.3f} ({results['accuracy']*100:.1f}%)")
        print(f"{'='*60}")
        
        if results['errors']:
            print(f"\n前5个错误示例:")
            for i, error in enumerate(results['errors'][:5]):
                print(f"\n错误 {i+1}:")
                print(f"问题: {error['question'][:100]}...")
                print(f"正确答案: {error['correct_answer']}")
                print(f"预测答案: {error['predicted_answer']}")
                print(f"原始响应: {error['raw_response']}")

def main():
    parser = argparse.ArgumentParser(description='MMLU评估程序')
    parser.add_argument('--base_url', default='http://127.0.0.1:18000/v1', help='API基础URL')
    parser.add_argument('--api_key', default='empty', help='API密钥')
    parser.add_argument('--model', default='/data/models/fazhi/DeepSeek-V3-0324-HF-FP4/', help='模型名称')
    parser.add_argument('--dataset_dir', default='datasets/mmlu', help='数据集目录')
    parser.add_argument('--output_dir', default='results', help='结果输出目录')
    parser.add_argument('--sample_size', type=int, default=None, help='每个数据集的采样大小')
    parser.add_argument('--datasets', nargs='+', default=None, help='指定要评估的数据集文件')
    
    args = parser.parse_args()
    
    # 创建评估器
    evaluator = MMLUEvaluator(args.base_url, args.api_key, args.model)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 获取要评估的数据集文件
    if args.datasets:
        dataset_files = [os.path.join(args.dataset_dir, f) for f in args.datasets]
    else:
        dataset_files = [
            os.path.join(args.dataset_dir, f) 
            for f in os.listdir(args.dataset_dir) 
            if f.endswith('.csv')
        ]
    
    overall_results = {
        'total_correct': 0,
        'total_questions': 0,
        'dataset_results': {},
        'timestamp': datetime.now().isoformat(),
        'config': {
            'base_url': args.base_url,
            'model': args.model,
            'sample_size': args.sample_size
        }
    }
    
    print(f"开始评估，共找到 {len(dataset_files)} 个数据集")
    print(f"模型: {args.model}")
    print(f"API: {args.base_url}")
    
    # 逐个评估数据集
    for dataset_file in dataset_files:
        if not os.path.exists(dataset_file):
            print(f"文件不存在: {dataset_file}")
            continue
            
        dataset_name = os.path.basename(dataset_file).replace('.csv', '')
        
        # 评估数据集
        results = evaluator.evaluate_dataset(dataset_file, args.sample_size)
        
        # 保存单个数据集结果
        output_file = os.path.join(args.output_dir, f"{dataset_name}_results.json")
        evaluator.save_results(results, output_file)
        
        # 打印摘要
        evaluator.print_summary(results, dataset_name)
        
        # 累加总体结果
        overall_results['total_correct'] += results['correct']
        overall_results['total_questions'] += results['total']
        overall_results['dataset_results'][dataset_name] = {
            'accuracy': results['accuracy'],
            'correct': results['correct'],
            'total': results['total']
        }
    
    # 计算总体准确率
    if overall_results['total_questions'] > 0:
        overall_accuracy = overall_results['total_correct'] / overall_results['total_questions']
        overall_results['overall_accuracy'] = overall_accuracy
        
        print(f"\n{'='*80}")
        print(f"总体评估结果:")
        print(f"总题数: {overall_results['total_questions']}")
        print(f"总正确数: {overall_results['total_correct']}")
        print(f"总体准确率: {overall_accuracy:.3f} ({overall_accuracy*100:.1f}%)")
        print(f"{'='*80}")
    
    # 保存总体结果
    overall_output_file = os.path.join(args.output_dir, 'overall_results.json')
    with open(overall_output_file, 'w', encoding='utf-8') as f:
        json.dump(overall_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n总体结果已保存到: {overall_output_file}")

if __name__ == "__main__":
    main() 