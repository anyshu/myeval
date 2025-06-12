# MMLU 模型评估程序

这是一个用于评估语言模型在MMLU（Massive Multitask Language Understanding）数据集上表现的程序。

## 功能特性

- 支持通过HTTP API调用模型进行评估
- 自动处理MMLU格式的CSV数据集
- 支持批量评估多个数据集
- 支持采样评估（减少评估时间）
- 详细的结果记录和错误分析
- 生成JSON格式的评估报告

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

使用默认配置运行：

```bash
python eval_mmlu.py
```

默认配置：
- API地址：http://127.0.0.1:18000/v1
- API密钥：empty
- 模型：/data/models/fazhi/DeepSeek-V3-0324-HF-FP4/
- 数据集目录：datasets/mmlu

### 自定义配置

```bash
python eval_mmlu.py \
    --base_url http://127.0.0.1:18000/v1 \
    --api_key "your_api_key" \
    --model "your_model_name" \
    --dataset_dir datasets/mmlu \
    --output_dir results
```

### 采样评估

如果数据集较大，可以使用采样评估：

```bash
python eval_mmlu.py --sample_size 20
```

### 评估特定数据集

```bash
python eval_mmlu.py --datasets abstract_algebra.csv
```

## 参数说明

- `--base_url`: API的基础URL
- `--api_key`: API密钥
- `--model`: 模型名称
- `--dataset_dir`: 数据集目录路径
- `--output_dir`: 结果输出目录
- `--sample_size`: 每个数据集的采样大小（None表示全部）
- `--datasets`: 指定要评估的数据集文件名（支持多个）

## 输出结果

程序会生成以下输出文件：

1. `results/{dataset_name}_results.json`: 单个数据集的详细结果
2. `results/overall_results.json`: 总体评估结果

### 结果文件格式

单个数据集结果包含：
- `correct`: 正确答案数量
- `total`: 总题目数量
- `accuracy`: 准确率
- `details`: 每道题的详细信息
- `errors`: 错误答案的详细信息

总体结果包含：
- `total_correct`: 总正确数
- `total_questions`: 总题目数
- `overall_accuracy`: 总体准确率
- `dataset_results`: 各数据集的结果摘要
- `config`: 评估配置信息

## 数据集格式

程序支持标准的MMLU CSV格式：

```csv
input,A,B,C,D,target
问题内容,选项A,选项B,选项C,选项D,正确答案
```

## 注意事项

1. 确保API服务正在运行且可访问
2. 程序会在API调用间添加0.1秒延迟以避免过于频繁的请求
3. 如果API调用失败，程序会继续运行其他题目
4. 建议先用小样本测试API连通性

## 示例输出

```
开始评估，共找到 1 个数据集
模型: /data/models/fazhi/DeepSeek-V3-0324-HF-FP4/
API: http://127.0.0.1:18000/v1

开始评估: datasets/mmlu/abstract_algebra.csv
进度: 1/100 - 正确: 1/1 (100.0%)
进度: 2/100 - 正确: 1/2 (50.0%)
...

============================================================
数据集: abstract_algebra
总题数: 100
正确数: 45
准确率: 0.450 (45.0%)
============================================================
``` # myeval
