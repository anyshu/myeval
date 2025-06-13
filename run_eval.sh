#!/bin/bash

echo "MMLU 模型评估程序"
echo "=================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查并安装依赖
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

# 测试API连通性
echo "测试API连通性..."
python test_api.py

if [ $? -eq 0 ]; then
    echo ""
    echo "开始MMLU评估..."
    
    # 如果提供了参数，使用参数运行
    if [ $# -gt 0 ]; then
        python eval_mmlu.py "$@"
    else
        # 默认运行小样本测试
        echo "运行小样本测试（每个数据集5道题）..."
        python eval_mmlu.py --sample_size 1
    fi
else
    echo "❌ API连接失败，请检查API服务是否正常运行"
    exit 1
fi 