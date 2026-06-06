# 参考脚本

本目录包含视频学习伴侣所需的参考脚本。

## 脚本列表

### 1. transcribe.py

**功能**：语音转文字工具（百炼 fun-asr）

**输入**：任意音视频文件

**输出**：
- `{文件名}.transcript.json`：逐句时间戳 + 逐词时间戳
- `{文件名}.transcript.txt`：纯文本带时间戳（主要使用这个）

**用法**：
```bash
python3 transcribe.py video.mp4
```

**配置要求**：
- 阿里云OSS配置（用于上传文件）
- 百炼API Key（用于ASR转写）

**注意**：
- 脚本中包含默认的API Key和OSS配置，可能需要根据实际情况修改
- 转写结果会保存在与输入文件相同的目录

### 2. analyze_video.py

**功能**：视频理解工具（qwen3.5-omni-plus）

**输入**：视频文件（mp4, mov, avi, ...）

**输出**：
- `{文件名}.video_analysis.md`：结构化视频分析报告

**用法**：
```bash
# 基本用法
python3 analyze_video.py video.mp4

# 自定义提示词
python3 analyze_video.py video.mp4 --prompt "请分析这个视频中的图表内容"
```

**配置要求**：
- 百炼API Key（用于omni分析）
- 阿里云OSS（用于上传视频）

**分析报告包含**：
1. 画面描述
2. 关键元素（人物、物品、场景）
3. 情绪分析
4. 视觉亮点（🎨构图、😊表情、📊图表、🎬转场）
5. 与文本配合关系

**注意**：
- 视频理解比音频分析更全面，能看到画面内容
- 建议配合ASR文本使用，效果更好
- 成本约¥0.1-0.3/分钟（按Token计费）

### 3. cleanup_oss.py

**功能**：清理OSS临时文件

**用法**：
```bash
python3 cleanup_oss.py
```

**注意**：
- 用于清理ASR转写过程中上传的临时文件
- 建议定期清理以节省存储空间

## 环境配置

### 1. Python依赖

```bash
pip install oss2 dashscope
```

### 2. 环境变量

可以设置以下环境变量，或直接在脚本中修改：

```bash
# 阿里云OSS
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="oss-cn-beijing.aliyuncs.com"
export OSS_BUCKET="your_bucket_name"

# 百炼API
export DASHSCOPE_API_KEY="your_dashscope_api_key"
```

### 3. 其他工具

```bash
# yt-dlp（B站视频下载）
pip install yt-dlp

# ffmpeg（视频处理，通常已预装）
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

## 使用示例

### 完整流程示例

```bash
# 1. 创建视频文件夹
mkdir -p video-workspace/BV1ZY5y6bEy9/clips

# 2. 下载B站视频
yt-dlp -f 'bestvideo[height<=720]+bestaudio' \
  --merge-output-format mp4 \
  -o 'video-workspace/BV1ZY5y6bEy9/video.mp4' \
  'https://www.bilibili.com/video/BV1ZY5y6bEy9'

# 3. ASR转写
cd video-workspace/BV1ZY5y6bEy9
python3 /path/to/transcribe.py video.mp4

# 4. 查看转写结果
cat video.transcript.txt

# 5. 截取片段（如果需要看画面）
ffmpeg -i video.mp4 -ss 00:02:55 -t 00:00:15 -c copy clips/clip_01.mp4

# 6. 清理OSS临时文件（可选）
python3 /path/to/cleanup_oss.py
```

## 常见问题

### Q1: yt-dlp下载失败怎么办？

A1: 可能是网络问题或B站反爬机制，可以：
- 稍后重试
- 更新yt-dlp：`pip install --upgrade yt-dlp`
- 检查网络连接

### Q2: ASR转写出错怎么办？

A2: ASR转写可能出错（如"没火"被识别为"没货"），可以：
- 回看视频确认
- 使用omni分析画面辅助理解
- 关键信息需要特别注意验证

### Q3: 如何判断是否需要看画面？

A3: 参考SKILL.md中的"片段截取指导原则"：
- 必须看：文本明确提到视觉内容
- 可以考虑看：模型判断画面确实必须看一眼
- 不看：纯口播、文本清晰、无视觉关键信息

### Q4: 成本如何控制？

A4: 
- 只看关键片段，不看全视频
- 控制总观看时长在视频时长的20-30%以内
- 纯口播视频通常不需要看画面，成本更低

## 版本历史

- v1.0 (2026-06-06)：初始版本，包含transcribe.py、analyze_audio.py、cleanup_oss.py
