# 有声书生态竞品研究（2026-06-12）

覆盖：服务器类 Audiobookshelf / Booksonic / Audioserve / Ting Reader；
生成类 Abogen / ebook2audiobook / easyVoice。资料来自各项目 GitHub/官网一手 README。

## 一、总览

| 项目 | 类型 | Stars | 技术栈 | 状态 |
|---|---|---|---|---|
| [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) | 生成 | **19.2k** | Python/Gradio | 非常活跃 |
| [Audiobookshelf](https://github.com/advplyr/audiobookshelf) | 服务器 | **13.2k** | Node+Vue, Docker | 非常活跃，事实标准 |
| [Abogen](https://github.com/denizsafak/abogen) | 生成 | 4.8k | Python, PyQt6+Flask | 活跃 |
| [easyVoice](https://github.com/cosin2077/easyVoice) | 生成 | 2.2k | Node+Vue | 活跃 |
| [Audioserve](https://github.com/izderadicka/audioserve) | 服务器 | 834 | **Rust**+Svelte | 小而专 |
| [Booksonic-Air](https://github.com/popeen/Booksonic-Air) | 服务器 | 224 | Java(Airsonic分支) | **2022年起停滞** |
| [Ting Reader](https://github.com/dqsq2e2/ting-reader) | 服务器 | 小型 | Docker 多架构 | 新晋国内 |

## 二、服务器类：管音频，不产音频

四者**均无 TTS 生成能力**，核心价值在收听体验：

- **Audiobookshelf（事实标准）**：书库管理（批量上传/元数据刮削/封面）、流式播放、**逐用户跨设备进度同步**、章节编辑、Web PWA + iOS/Android 客户端、开放 API + RSS、多用户权限。生成类工具（如 Abogen）已开始内置"推送到 Audiobookshelf"集成
- **Audioserve**：极简哲学——拒绝音频标签，**目录结构即导航**；Rust 高性能、Opus 三档转码、共享密钥认证（无账户体系）。"几千本书、几个用户"的个人定位
- **Booksonic**：Subsonic→Airsonic 血统的老牌方案，兼容 Subsonic API 生态，但已停滞，用户被 Audiobookshelf 虹吸
- **Ting Reader**：国内场景的轻量自托管（元数据刮削/进度同步/多架构 Docker），定位"中文 Audiobookshelf 平替"

## 三、生成类：三种路线，无人做"自动多角色"

| 维度 | Abogen | ebook2audiobook | easyVoice |
|---|---|---|---|
| TTS | Kokoro-82M（单引擎，快） | **8 引擎**（XTTSv2/Bark/VITS/Tortoise…） | Edge-TTS/Azure + OpenAI 兼容 API |
| 克隆 | ✗（语音混音器替代） | ✓ zero-shot（自传音频） | ✗ |
| 多角色 | ✗ 单声 | **手工标签** `[voice:path]` 切换 | **LLM 段落级**推荐配音参数 |
| 说话人识别 | ✗ | ✗（人工标） | 粗粒度（段落，非逐句归属） |
| 章节 | 标记语法 `<<CHAPTER_MARKER>>` | EPUB/MOBI 自动检测 | - |
| 字幕 | **SRT/ASS 多级同步字幕**（词级） | - | 自动字幕 |
| 输出 | WAV/MP3/**M4B(带章节)** | **9 格式含 m4b/m4a** | MP3 + 流式 |
| 输入 | EPUB/PDF/TXT/MD/SRT | EPUB/MOBI/PDF(**OCR**) | TXT |
| 形态 | 桌面 GUI + Web UI、队列批处理 | Gradio Web + CLI + Docker/HF Spaces | 前后端分离 Web，Docker |
| 其他 | **LLM 文本规范化、Audiobookshelf 集成** | 1158 语言、2GB RAM 可跑 | 10万字一键转、流式即听 |

## 四、对 voicebook 的启示

### 差异化确认：自动多角色是真空地带
19.2k stars 的 ebook2audiobook 让用户**手工**给每句标 `[voice:path]`；easyVoice 用 LLM 做**段落级**参数推荐。
**没有任何头部项目做"逐句说话人识别 + 画像自动选角"**——我们的 L1规则+L2 CSI+L3画像 流水线（金标93%）是真实的护城河。
（小众的 easytts 做了 RoBERTa 逐句识别但停留在工具层，无生态位。）

### 必须补齐的"行业标配"（差距清单，按优先级）
1. **M4B 输出**（我们现在是 mp4；m4b=章节+书签+封面元数据的有声书标准容器，ffmpeg 一行切换）
2. **Audiobookshelf 集成/兼容**：产物带规范元数据，自托管听书的接收端是它（以及国内 Ting Reader）
3. **同步字幕**（Abogen 的杀手锏，SRT 起步）
4. **EPUB 输入**（书源大多是 epub，我们已在测试语料里做过提取器）
5. 队列/断点续传/批处理（整本书生产必需）
6. Web UI（成熟期再说）

### 生态位判断
"生成→收听"管道正在打通（Abogen→Audiobookshelf）。voicebook 的合理位置：
**多角色有声书生成引擎**，产物即插即用进 Audiobookshelf/Ting Reader；
且 talebook（自有书库服务器）+ voicebook 天然构成国内无人占据的"书库→AI有声化→收听"闭环。
