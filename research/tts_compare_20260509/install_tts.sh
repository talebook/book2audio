#!/bin/bash

set -e  # 出错即停止

echo "========================================"
echo "  book2audio TTS 安装脚本"
echo "========================================"
echo ""

# 项目目录
PROJECT_DIR="/Users/bytedance/code/book2audio"
cd "$PROJECT_DIR"

# 检查 Python 版本
echo "检查 Python 版本..."
PYTHON_CMD=$(which python3 || which python)
$PYTHON_CMD --version

echo ""
echo "配置 pip 使用清华源..."
$PYTHON_CMD -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "升级 pip..."
$PYTHON_CMD -m pip install --upgrade pip

echo ""
echo "安装基础依赖..."
$PYTHON_CMD -m pip install numpy scipy soundfile psutil tqdm requests

echo ""
echo "安装 PyTorch..."
$PYTHON_CMD -m pip install torch torchaudio

echo ""
echo "安装 kokoro-onnx..."
$PYTHON_CMD -m pip install kokoro-onnx

echo ""
echo "克隆并安装 CosyVoice..."
if [ -d "temp_cosyvoice" ]; then
    echo "CosyVoice 已克隆，跳过..."
else
    git clone --depth 1 https://github.com/FunAudioLLM/CosyVoice.git temp_cosyvoice
fi

cd temp_cosyvoice
$PYTHON_CMD -m pip install -e .
$PYTHON_CMD -m pip install transformers
cd ..

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "验证安装..."

$PYTHON_CMD -c "
import sys
print('Python 版本:', sys.version)

try:
    import numpy
    print('✅ numpy:', numpy.__version__)
except Exception as e:
    print('❌ numpy:', e)

try:
    import torch
    print('✅ torch:', torch.__version__)
except Exception as e:
    print('❌ torch:', e)

try:
    from kokoro_onnx import Kokoro
    print('✅ kokoro-onnx: 已安装')
except Exception as e:
    print('❌ kokoro-onnx:', e)

try:
    from cosyvoice.cli.cosyvoice import CosyVoice
    print('✅ CosyVoice: 已安装')
except Exception as e:
    print('❌ CosyVoice:', e)
"

echo ""
echo "========================================"
echo "  现在可以运行 TTS 测试了！"
echo "========================================"
echo ""
echo "运行测试命令："
echo "  python3 test_tts_comprehensive.py"
echo ""
