# book2audio 智能有声书工具

将小说 TXT 转化为多角色有声书：识别对白/旁白与说话人，按角色匹配音色合成语音，输出带章节标记的 MP4 有声书。

## 快速开始

```bash
uv sync
uv run python -m book2audio -i book/xuanjian.txt -c 1-3 -o output/xuanjian_ch1-3.mp4
```

参数：
- `-i/--input` 小说 TXT（UTF-8）
- `-c/--chapters` 章节范围，如 `1-3` 或 `5`（默认 `1-3`）
- `-o/--output` 输出 MP4 路径
- `--keep-temp` 保留中间音频

依赖：`ffmpeg`（`brew install ffmpeg`）。

## 当前流水线（v0.1，edge-tts 基线）

```
TXT → 章节分割（正则） → 对白/旁白切分（引号规则） → edge-tts 双音色合成 → ffmpeg 拼接 → MP4（带章节标记）
```

- 旁白：`zh-CN-YunjianNeural`；对白：`zh-CN-YunxiNeural`
- 说话人识别（按角色分配音色）和高真人感 TTS 后端见路线图

## 目录结构

```
src/book2audio/     流水线源码（parser / pipeline / CLI）
book/               小说素材
research/           历次调研归档（LLM benchmark、TTS 对比、角色画像 demo、选型重审）
.planning/          项目规划（PROJECT / ROADMAP / STATE）
tests/              评测记录
```

## 路线图（摘要）

1. ✅ edge-tts 端到端基线（本版本）
2. 程序化说话人识别库：规则层 + CSI 专用模型（见 `research/tech_reselect_20260610/`）
3. 高真人感 TTS：CosyVoice3-0.5B 主线，IndexTTS-2 / 豆包 API 备选
4. 角色画像 → 音色自动映射；年龄变化音色过渡
5. 背景音/环境音（P2）
