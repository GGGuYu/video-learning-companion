#!/usr/bin/env python3
"""
视频理解工具 — qwen3.5-omni-plus (OpenAI 兼容)
===============================================
输入:  视频文件 (mp4, mov, avi, ...)
输出:  {文件名}.video_analysis.md  — 结构化分析报告

流程:  上传 OSS → 生成预签名 URL → 调 omni 视频分析 → 输出报告

用法:  python3 analyze_video.py video.mp4
       python3 analyze_video.py video.mp4 --prompt "请分析这个视频的画面内容"
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

import oss2
import dashscope
from openai import OpenAI

# ============================================================
# 配置
# ============================================================
OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET = os.environ.get("OSS_BUCKET", "")

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODEL = "qwen3.5-omni-plus"

DEFAULT_PROMPT = """请仔细分析这段视频，完成以下任务：

1. 【画面描述】用 3-5 句话描述视频的主要画面内容。

2. 【关键元素】识别视频中的关键元素：
   - 人物：数量、表情、动作、情绪状态
   - 物品：重要的物品、道具、背景元素
   - 场景：环境、光线、构图特点

3. 【情绪分析】分析视频中的情绪变化：
   - 开头情绪
   - 中间变化
   - 结尾情绪
   - 情绪高点（如果有）

4. 【视觉亮点】标记以下特殊时刻：
   - 🎨 画面构图精彩的地方
   - 😊 表情/动作特别生动的地方
   - 📊 图表/数据/文字出现的地方
   - 🎬 转场/剪辑特别的地方

5. 【关键信息】提取视频中的关键信息：
   - 提到的重要概念、观点、结论
   - 显示的文字、数据、图表内容
   - 重要的时间点、数字、人名等

请用结构化 Markdown 格式输出。"""


def _oss_client():
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    return oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET)


def _upload_oss(file_path: str) -> tuple:
    """上传到 OSS，使用文件 hash 避免重复上传。返回 (object_name, presigned_url)"""
    import hashlib
    fp = Path(file_path)
    # 计算 MD5
    md5 = hashlib.md5()
    with open(fp, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    h = md5.hexdigest()[:8]

    bucket = _oss_client()
    object_name = f"temp/{fp.name}_{h}"

    # 检查是否已存在
    try:
        bucket.head_object(object_name)
        print(f"📤 OSS 已存在，跳过上传: {object_name}")
    except:
        print(f"📤 上传 OSS: {object_name} ... ", end="", flush=True)
        t0 = time.time()
        bucket.put_object_from_file(object_name, str(fp))
        print(f"✓ ({time.time()-t0:.1f}s)")

    url = bucket.sign_url("GET", object_name, 7200)
    return object_name, url


def analyze_video(file_path: str, prompt: str = None):
    fp = Path(file_path).resolve()
    if not fp.is_file():
        print(f"❌ 文件不存在: {fp}")
        sys.exit(1)

    file_size_mb = fp.stat().st_size / 1024 / 1024
    print(f"📁 {fp.name}  ({file_size_mb:.1f}MB)")

    # ---- 1. 上传 OSS ----
    object_name, presigned_url = _upload_oss(str(fp))

    # ---- 2. 准备提示词 ----
    if prompt is None:
        prompt = DEFAULT_PROMPT

    # ---- 3. 调 omni (OpenAI 兼容) ----
    print(f"🤖 调用 {MODEL} (视频理解) ...\n")

    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    full_text = ""
    usage_info = None

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": presigned_url
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            stream=True,
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                print(text, end="", flush=True)
                full_text += text
            if chunk.usage:
                usage_info = chunk.usage

    except Exception as e:
        print(f"\n❌ 调用失败: {e}")
        return None

    # ---- 4. 保存报告 ----
    out_path = fp.with_suffix(".video_analysis.md")
    header = (f"# 视频分析报告\n"
              f"**文件**: {fp.name}\n"
              f"**分析时间**: {datetime.now().isoformat(timespec='seconds')}\n"
              f"**模型**: {MODEL}\n\n")
    out_path.write_text(header + full_text, encoding="utf-8")
    print(f"\n📄 报告已保存: {out_path}")

    if usage_info:
        print(f"💰 Token: {usage_info}")

    return full_text


def main():
    parser = argparse.ArgumentParser(description="视频理解工具")
    parser.add_argument("file_path", help="视频文件路径")
    parser.add_argument("--prompt", help="自定义提示词", default=None)
    
    args = parser.parse_args()
    
    analyze_video(args.file_path, args.prompt)


if __name__ == "__main__":
    main()
