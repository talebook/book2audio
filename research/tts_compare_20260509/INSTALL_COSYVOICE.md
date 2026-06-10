# CosyVoice 和 kokoro-onnx 本地安装指南

## 环境准备

你的当前环境：
- Python 版本：3.9.6
- 模型文件已下载：✅
  - `pretrained_models/CosyVoice-300M-SFT/
  - `models/kokoro-v1.0.onnx`

## 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
cd /Users/bytedance/code/book2audio

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 配置 pip 使用清华源（如果在国内）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 安装必要依赖

```bash
# 基础依赖
pip install numpy scipy soundfile psutil
```

### 3. 安装 PyTorch（支持 CosyVoice）

```bash
# macOS 安装 PyTorch（CPU 版本）
pip install torch torchaudio

# 如果你有 M1/M2/M3 芯片，可以使用官方安装命令：
# pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 4. 安装 kokoro-onnx

```bash
pip install kokoro-onnx
```

### 5. 克隆并安装 CosyVoice

```bash
# 克隆 CosyVoice 仓库
cd /Users/bytedance/code/book2audio
git clone --depth 1 https://github.com/FunAudioLLM/CosyVoice.git temp_cosyvoice

# 安装 CosyVoice
cd temp_cosyvoice
pip install -e .

# 安装额外需要的 transformers
pip install transformers

cd ..
```

## 验证安装是否成功，运行：

```bash
python3 -c "
from kokoro_onnx import Kokoro
from cosyvoice.cli.cosyvoice import CosyVoice
print('✅ 所有依赖已安装成功！')
"
```

## 运行 TTS 测试

```bash
python3 test_tts_comprehensive.py
```

## 快速安装失败的备选方案

如果上述方法失败，也可以使用 requirements.txt 文件批量安装：

```bash
pip install -r requirements.txt
```
