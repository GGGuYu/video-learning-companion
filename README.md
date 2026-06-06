# 🎬 Video Learning Companion

> **视频学习伴侣**：与AI一起看视频、互动讨论、沉淀经验

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/GGGuYu/video-learning-companion)](https://github.com/GGGuYu/video-learning-companion/stargazers)

## 📖 简介

**Video Learning Companion** 是一个AI驱动的视频学习工具，帮助你从视频中高效提取知识。

### 🎯 核心理念

- **按需深入**：AI不是被动地看完整视频，而是只在关键片段深入分析
- **成本可控**：总观看时长控制在视频时长的20-30%以内
- **知识沉淀**：最终产出是结构化的知识经验，不是视频转写

### 💡 解决的问题

| 传统方式 | Video Learning Companion |
|:---------|:-------------------------|
| 被动观看，信息过载 | 主动提问，按需深入 |
| 看完就忘，知识碎片化 | 互动讨论，结构化沉淀 |
| AI看完整视频，成本高昂 | 只看关键片段，成本可控 |

## ✨ 功能特点

### 🎬 视频下载
- 支持B站视频下载（无需登录）
- 自动选择720p画质（够用且节省空间）
- 使用yt-dlp，支持数千个视频网站

### 📝 ASR转写
- 使用阿里云百炼fun-asr模型
- 生成带时间戳的纯文本（秒级精度）
- 成本约¥0.8/小时

### 🎥 视频理解
- 使用qwen3.5-omni-plus模型
- 分析画面内容、情绪变化、视觉亮点
- 成本约¥7/百万Token（按需使用）

### 💬 互动讨论
- 用户边看视频边提问
- AI从文本定位时间段
- 智能判断是否需要看画面

### 📊 知识沉淀
- 生成结构化的分析报告
- 提取关键信息和洞察
- 支持多种输出格式

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/GGGuYu/video-learning-companion.git
cd video-learning-companion
```

### 2. 安装依赖

```bash
# Python依赖
pip install oss2 dashscope openai yt-dlp

# 系统工具（macOS）
brew install ffmpeg

# 系统工具（Ubuntu）
sudo apt install ffmpeg
```

### 3. 配置环境变量

```bash
# 阿里云百炼API
export DASHSCOPE_API_KEY="sk-xxxxx"

# 阿里云OSS
export OSS_ACCESS_KEY_ID="LTAIxxxxxx"
export OSS_ACCESS_KEY_SECRET="xxxxxx"
export OSS_BUCKET="your-bucket"
```

### 4. 测试运行

```bash
# 复制脚本到工作目录
cp references/transcribe.py /path/to/your/workspace/
cp references/analyze_video.py /path/to/your/workspace/

# 下载B站视频
yt-dlp -f 'bestvideo[height<=720]+bestaudio' \
  --merge-output-format mp4 \
  -o 'video.mp4' \
  'https://www.bilibili.com/video/BV...'

# ASR转写
python3 transcribe.py video.mp4

# 视频理解（可选）
python3 analyze_video.py video.mp4
```

## 📁 文件结构

```
video-learning-companion/
├── SKILL.md                    # HanaAgent Skill文档（含元数据）
├── design.md                   # 设计文档（动机、目标、边界情况）
├── README.md                   # 本文件
└── references/
    ├── README.md               # 脚本使用说明
    ├── transcribe.py           # ASR转写脚本
    └── analyze_video.py        # 视频理解脚本
```

## 📚 文档说明

| 文档 | 用途 | 目标读者 |
|:-----|:-----|:---------|
| **README.md** | 项目介绍、快速开始 | 所有用户 |
| **SKILL.md** | HanaAgent Skill规范 | AI Agent |
| **design.md** | 设计动机、技术细节、维护指南 | 开发者、维护者 |
| **references/README.md** | 脚本使用说明 | 使用脚本的用户 |

## 🔧 配置说明

### 阿里云百炼API

**获取方式**：
1. 注册[阿里云账号](https://www.aliyun.com/)
2. 开通[百炼服务](https://dashscope.aliyun.com/)
3. 获取API Key

**需要开通的模型**：
| 模型 | 用途 | 计费方式 |
|:-----|:-----|:---------|
| fun-asr | 语音转文字 | ¥0.00022/秒 |
| qwen3.5-omni-plus | 视频理解 | ¥7/百万Token |

### 阿里云OSS

**获取方式**：
1. 在[阿里云控制台](https://oss.console.aliyun.com/)创建OSS Bucket
2. 获取AccessKey ID和Secret
3. 配置Bucket权限（建议私有读写）

**为什么需要OSS**：
- 百炼API要求文件通过URL访问
- 本地文件需要先上传到OSS，获取预签名URL
- 空桶不收费，存储费约¥0.12/GB/月

## 📊 成本参考

| 视频长度 | ASR成本 | 视频理解成本 | 总成本 |
|:---------|:--------|:-------------|:-------|
| 3分钟 | ¥0.16 | ¥0-0.3 | ¥0.16-0.46 |
| 10分钟 | ¥0.53 | ¥0.3-0.8 | ¥0.83-1.33 |
| 20分钟 | ¥1.06 | ¥0.5-1.5 | ¥1.56-2.56 |
| 30分钟 | ¥1.59 | ¥1-2 | ¥2.59-3.59 |

**成本控制策略**：
- 只看关键片段，不看全视频
- 总观看时长控制在视频时长的20-30%以内
- 纯口播视频通常不需要看画面

## 🎯 使用场景

### ✅ 支持的场景

- 📚 **学习型视频**：教程、课程、讲解
- 📊 **分析型视频**：数据分析、技术分析、市场分析
- 💬 **讨论型视频**：观点分享、访谈、播客
- 🎬 **生活记录**：Vlog、日常记录

### ❌ 不支持的场景

- 纯娱乐视频（无学习价值）
- 需要实时处理的直播
- 需要登录才能访问的私密视频

## 🤝 贡献指南

欢迎贡献代码、文档或提出建议！

### 如何贡献

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 贡献方向

- 支持更多视频平台（YouTube、抖音等）
- 优化提示词，提高分析质量
- 添加批量处理功能
- 知识图谱整合
- 复习提醒功能

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载工具
- [阿里云百炼](https://dashscope.aliyun.com/) - AI模型服务
- [HanaAgent](https://github.com/liliMozi/openhanako) - AI Agent平台

## 📞 联系方式

- GitHub: [GGGuYu](https://github.com/GGGuYu)
- 项目地址: [video-learning-companion](https://github.com/GGGuYu/video-learning-companion)

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**
