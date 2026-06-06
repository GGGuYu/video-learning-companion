---
name: video-learning-companion
description: "Video learning companion for watching, discussing, and extracting knowledge from videos together. Use when users want to watch a video with AI, discuss its content, extract key insights, and build structured knowledge. Supports Bilibili video download, ASR transcription, video understanding, and knowledge distillation. Ideal for learning from tutorials, analysis videos, lectures, and other educational content."
argument-hint: "[video_url] [question]"
user-invocable: true
allowed-tools:
  - Bash(python3 *)
  - Bash(ffmpeg *)
  - Bash(yt-dlp *)
license: MIT
---

# Video Learning Companion

视频学习伴侣：一起看视频、互动讨论、沉淀经验

## 核心定位

这是一个**视频学习伴侣**技能，帮助用户与AI一起观看学习型视频（如教程、分析、讲解等），通过互动讨论沉淀知识和经验。

**核心价值**：
- 不是简单地"看视频"，而是**有目的地学习**
- AI不是被动地看完整视频，而是**按需深入关键片段**
- 最终产出是**结构化的知识沉淀**，而不是视频转写

## When to Use This Skill

Use this skill when users request:

- "一起看这个视频"
- "帮我分析这个视频"
- "我想从这个视频学习"
- "这个视频讲了什么"
- "帮我提取视频里的关键信息"
- "讨论一下这个视频"
- "沉淀一下这个视频的经验"

**Supported scenarios:**
- 📚 **学习型视频**：教程、课程、讲解
- 📊 **分析型视频**：数据分析、技术分析、市场分析
- 💬 **讨论型视频**：观点分享、访谈、播客
- 🎬 **生活记录**：Vlog、日常记录

**Not supported:**
- 纯娱乐视频（无学习价值）
- 需要实时处理的直播
- 需要登录才能访问的私密视频

## 工作流程

```
用户传入B站视频链接
        │
        ▼
① 下载视频（yt-dlp）
        │
        ▼
② ASR转写（transcribe.py）
        │
        ▼
③ 用户边看视频边提问
        │
        ▼
④ AI从文本定位时间段
        │
        ▼
⑤ 判断是否需要看画面
        │
    ┌───┴───┐
    ▼       ▼
  不看     看画面
    │       │
    │   ⑥ 截取片段（ffmpeg）
    │       │
    │   ⑦ omni分析画面
    │       │
    └───┬───┘
        ▼
⑧ 讨论并沉淀经验
```

## 文件夹结构

在工作目录下创建 `video-workspace/` 文件夹，每个视频一个子文件夹：

```
video-workspace/
└── {BV号}/
    ├── video.mp4                    # 原始视频
    ├── transcript.txt               # ASR文本带时间戳（主要使用这个）
    ├── analysis_summary.md          # 汇总分析报告（所有片段的分析汇总）
    └── clips/                       # 截取的片段（如果有）
        ├── 01_描述.mp4              # 截取的视频片段
        ├── 01_描述.video_analysis.md # 该片段的视频理解结果
        ├── 02_描述.mp4
        └── 02_描述.video_analysis.md
```

**命名规范**：
- 文件夹名：使用B站视频的BV号（如 `BV1ZY5y6bEy9`）
- 视频文件：统一命名为 `video.mp4`
- 转写文件：`video.transcript.txt`（主要使用，不需要json）
- 片段文件：`{编号}_{描述}.mp4`（如 `01_emotional_moment.mp4`）
- 片段分析：`{编号}_{描述}.video_analysis.md`
- 汇总报告：`analysis_summary.md`（汇总所有片段的分析结果）

**文件清理**：
- `transcript.json`：不需要，可以删除（我们只用txt）
- 定期清理clips目录中的临时片段

## 参考脚本（references目录）

本Skills提供了完整的参考脚本，位于`references/`目录中：

```
references/
├── README.md               # 脚本使用说明
├── transcribe.py           # ASR转写脚本
└── analyze_video.py        # 视频理解脚本
```

### 脚本说明

| 脚本 | 功能 | 用途 |
|:-----|:-----|:-----|
| transcribe.py | ASR转写（百炼 fun-asr） | 语音转文字，生成带时间戳的文本 |
| analyze_video.py | 视频理解（qwen3.5-omni-plus） | 分析视频画面，提取关键信息 |

### 如何使用这些脚本

**1. 复制脚本到工作目录**：
```bash
cp references/transcribe.py /path/to/your/workspace/
cp references/analyze_video.py /path/to/your/workspace/
```

**2. 配置环境变量**：
```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
export OSS_ACCESS_KEY_ID="your_oss_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_oss_access_key_secret"
export OSS_BUCKET="your_oss_bucket"
```

**3. 运行脚本**：
```bash
# ASR转写
python3 transcribe.py video.mp4

# 视频理解
python3 analyze_video.py video.mp4
```

### 如果脚本无法运行

**常见问题**：
1. **环境变量未设置**：检查是否正确设置了所有必需的环境变量
2. **依赖未安装**：运行`pip install oss2 dashscope openai`
3. **OSS配置错误**：检查Bucket名称、AccessKey是否正确
4. **API Key无效**：检查百炼API Key是否有效

**详细配置说明**：请参考`references/README.md`和`design.md`中的配置要求章节。

## 配置要求

### 1. 环境依赖

```bash
# yt-dlp（B站视频下载）
pip install yt-dlp

# Python依赖（用于ASR转写和视频理解）
pip install oss2 dashscope openai

# ffmpeg（视频处理，通常已预装）
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### 2. API配置

**只需要一个阿里云百炼API Key**，但需要开通两个模型：

| 模型 | 用途 | 计费方式 |
|:-----|:-----|:---------|
| fun-asr | 语音转文字 | ¥0.00022/秒 |
| qwen3.5-omni-plus | 视频理解 | ¥7/百万Token（视频帧） |

**环境变量配置**：
```bash
# 阿里云百炼API
export DASHSCOPE_API_KEY="sk-xxxxx"

# 阿里云OSS（用于上传大文件）
export OSS_ACCESS_KEY_ID="LTAIxxxxxx"
export OSS_ACCESS_KEY_SECRET="xxxxxx"
export OSS_BUCKET="your-bucket"
```

### 3. 获取配置

**阿里云百炼API Key**：
1. 注册阿里云账号
2. 开通百炼服务
3. 获取API Key

**阿里云OSS配置**：
1. 在阿里云控制台创建OSS Bucket
2. 获取AccessKey ID和Secret
3. 配置Bucket权限（建议私有读写）

**详细配置指南**：请参考`design.md`中的"配置要求"章节。

## 详细步骤

### 步骤1：下载B站视频

```bash
# 创建视频文件夹
mkdir -p video-workspace/{BV号}/clips

# 下载视频（720p，无需登录）
yt-dlp -f 'bestvideo[height<=720]+bestaudio' \
  --merge-output-format mp4 \
  -o 'video-workspace/{BV号}/video.mp4' \
  'https://www.bilibili.com/video/{BV号}'
```

**注意事项**：
- yt-dlp不需要登录B站账号
- 720p画质完全够用（看文字、图表没问题）
- 如果下载失败，可能是网络问题，稍后重试

### 步骤2：ASR转写

```bash
cd video-workspace/{BV号}
python3 /path/to/transcribe.py video.mp4
```

**产出**：
- `video.transcript.json`：详细结果（逐词时间戳，62KB）
- `video.transcript.txt`：纯文本带时间戳（2.5KB，主要使用这个）

**ASR错误处理**：
- ASR转写可能出错（如"没火"被识别为"没货"）
- 如果文本语义不通顺，可能需要回看视频确认
- 关键信息（人名、地名、专业术语）需要特别注意验证

### 步骤3：用户边看视频边提问

用户在观看视频过程中，可以随时提问：
- "刚才那个部分讲了什么？"
- "10:30那里说的是什么意思？"
- "他提到的那个概念是什么？"

### 步骤4：AI从文本定位时间段

AI从 `video.transcript.txt` 中定位相关时间段：

```txt
[00:00:00 - 00:00:06] 啊，传来噩耗，刚刚在回家的路上被同事们给刷到了，这下算是完蛋了！
[00:00:06 - 00:00:10] 我都还没火呢，这没火怎么就就把我刷到了呀？
```

**定位方法**：
- 根据用户提问的关键词，在文本中搜索
- 找到相关时间段，返回给用户确认
- 如果用户描述模糊，可以提供多个候选时间段

### 步骤5：判断是否需要看画面

**三档判断标准**：

#### 必须看（文本明确提到视觉内容）
- "大家看这个图表"
- "这里是演示/操作步骤"
- "这个界面/画面显示"
- 提到具体数据、图表、演示、操作步骤等

#### 可以考虑看（模型判断画面确实必须看一眼）
- ASR文本语义不通顺，可能出错需要验证
- 讲到关键概念、核心观点，但不确定画面是否有补充信息
- 转折点、结论部分，但需要模型判断画面是否重要
- **ASR文本令人困惑**：文本读起来不通顺、不合逻辑、与上下文不匹配
  - 可能是ASR识别错误（如"没火"被识别为"没货"）
  - 可能是口语化表达导致文本不连续
  - 可能是画面与文本配合，需要看画面才能理解
  - 这种情况下，建议截取该片段，用视频理解来验证和补充

#### 不看（默认）
- 纯口播，内容主要是语言表达
- 文本已经足够清晰，不需要画面辅助
- 熟悉的领域，不需要画面补充
- 生活记录、情感表达、故事叙述等

### 步骤6：截取片段（如果需要看画面）

```bash
# 截取指定时间段的视频片段
ffmpeg -i video.mp4 -ss 00:02:55 -t 00:00:15 -c copy clips/clip_01.mp4
```

**参数说明**：
- `-ss`：开始时间（格式：HH:MM:SS）
- `-t`：持续时长（秒）
- `-c copy`：直接复制，不重新编码（快速）

### 步骤7：omni分析画面（如果需要看画面）

使用 `analyze_video.py` 分析截取的片段。

**用法**：
```bash
# 基本用法
python3 analyze_video.py clips/emotional_moment.mp4

# 自定义提示词
python3 analyze_video.py clips/emotional_moment.mp4 --prompt "请分析这个视频中的图表内容"
```

**提示词设计**：
- 针对不同视频类型定制提示词
- 关注画面中的关键信息（图表、数据、操作步骤等）
- 结合ASR文本进行综合分析

**分析报告包含**：
1. 画面描述
2. 关键元素（人物、物品、场景）
3. 情绪分析
4. 视觉亮点
5. 与文本配合关系

### 步骤8：讨论并沉淀经验

基于文本和画面分析，与用户进行讨论：

**讨论要点**：
- 视频的核心观点是什么？
- 有哪些关键信息需要记录？
- 有哪些可以应用到实际工作中的经验？
- 有哪些需要进一步验证或研究的内容？

**沉淀形式**：
- 对话式笔记（像我们现在这样的讨论记录）
- 结构化摘要（带时间戳的知识点列表）
- 可执行洞察（针对具体领域的行动建议）

## 片段截取指导原则

### 按视频长度分级

| 视频长度 | 建议看片段数 | 每段时长 | 总观看时长 |
|:---------|:------------|:---------|:-----------|
| ≤3分钟 | 0-2个 | 30秒-2分钟 | 0-3分钟 |
| 3-10分钟 | 1-3个 | 30秒-2分钟 | 2-5分钟 |
| 10-20分钟 | 2-4个 | 30秒-2分钟 | 4-8分钟 |
| 20-30分钟 | 3-5个 | 30秒-2分钟 | 6-10分钟 |
| 30分钟以上 | 4-6个 | 30秒-2分钟 | 8-12分钟 |

**核心原则**：总观看时长控制在视频时长的**20-30%**以内。

### 每段时长决定因素

模型根据以下因素决定每段时长：
- **内容密度**：信息量大就截长一点（1-2分钟）
- **话题完整性**：确保截取完整的讨论单元
- **画面变化**：如果画面频繁切换，可能需要更长时间理解
- **一般情况**：30秒-1分钟足够

### 成本控制

| 视频长度 | 看片段数 | 预估成本 |
|:---------|:---------|:---------|
| 3分钟 | 1个 | ¥0.1-0.3 |
| 10分钟 | 2-3个 | ¥0.3-0.8 |
| 20分钟 | 3-4个 | ¥0.5-1.5 |
| 30分钟 | 4-5个 | ¥1-2 |

**成本说明**：
- omni视频分析按Token计费（约7元/百万Token）
- 只看关键片段而不是全视频，成本可控
- 纯口播视频通常不需要看画面，成本更低

## 测试建议

### 首次测试

1. **选择短视频**：建议选择3-5分钟的短视频进行首次测试
2. **验证完整流程**：下载 → ASR转写 → 定位时间段 → 判断是否看画面 → 讨论
3. **记录问题**：记录遇到的问题和改进建议

### 测试用例

**测试用例1：纯口播视频**
- 验证：是否正确判断"不需要看画面"
- 预期：只使用ASR文本进行讨论

**测试用例2：教程类视频**
- 验证：是否正确识别"必须看画面"的部分
- 预期：截取关键操作步骤的片段

**测试用例3：数据分析视频**
- 验证：是否正确识别图表、数据等视觉内容
- 预期：截取包含图表的片段进行分析

## 注意事项

### ASR转写错误

- ASR转写可能出错（如"没火"被识别为"没货"）
- 如果文本语义不通顺，可能需要回看视频确认
- 关键信息（人名、地名、专业术语）需要特别注意验证

### 画面重要性判断

- 不是所有视频都需要看画面
- 纯口播视频通常不需要看画面
- 只有明确提到视觉内容时才需要看画面

### 成本控制

- 只看关键片段，不看全视频
- 控制总观看时长在视频时长的20-30%以内
- 纯口播视频成本最低

### 用户体验

- 用户主导观看节奏，AI按需深入
- 不要过度分析，保持讨论的自然流畅
- 最终产出是知识沉淀，而不是视频分析报告

## 扩展功能

### 1. 批量处理

可以批量下载和处理多个视频：
```bash
# 批量下载
for bv in BV1xxx BV2xxx BV3xxx; do
  yt-dlp -f 'bestvideo[height<=720]+bestaudio' \
    --merge-output-format mp4 \
    -o "video-workspace/${bv}/video.mp4" \
    "https://www.bilibili.com/video/${bv}"
done
```

### 2. 知识图谱

将多个视频的讨论结果整合成知识图谱：
- 提取关键概念和观点
- 建立概念之间的关联
- 形成结构化的知识体系

### 3. 复习提醒

根据遗忘曲线，定期提醒用户复习：
- 1天后复习
- 3天后复习
- 7天后复习
- 30天后复习

## 版本历史

- v1.0 (2026-06-06)：初始版本，基于B站视频的学习伴侣功能
