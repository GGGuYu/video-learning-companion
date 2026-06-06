#!/usr/bin/env python3
"""
语音转文字工具 — 百炼 fun-asr (异步)
=====================================
输入:  任意音视频文件
输出:  {文件名}.transcript.json  — 逐句时间戳 + 逐词时间戳
       {文件名}.transcript.txt   — 纯文本

流程:  上传 OSS → 提交异步转写 → 轮询完成 → 下载 JSON → 删 OSS 文件

用法:  python3 transcribe.py meeting.m4a
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from http import HTTPStatus
from urllib import request as url_request

import oss2
import dashscope
from dashscope.audio.asr import Transcription

# ============================================================
# 配置
# ============================================================
OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET = os.environ.get("OSS_BUCKET", "")

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODEL = "fun-asr"


def _oss_client():
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    return oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET)


def _upload_oss(file_path: str) -> tuple:
    """上传到 OSS，使用文件 hash 避免重复上传。返回 (object_name, presigned_url)"""
    import hashlib
    fp = Path(file_path)
    md5 = hashlib.md5()
    with open(fp, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    h = md5.hexdigest()[:8]

    bucket = _oss_client()
    object_name = f"temp/{fp.name}_{h}"

    try:
        bucket.head_object(object_name)
        print(f"📤 OSS 已存在，跳过上传: {object_name}")
    except:
        print(f"📤 上传 OSS ... ", end="", flush=True)
        t0 = time.time()
        bucket.put_object_from_file(object_name, str(fp))
        print(f"✓ ({time.time()-t0:.1f}s)")

    return object_name, bucket.sign_url("GET", object_name, 7200)


def transcribe_file(file_path: str):
    fp = Path(file_path).resolve()
    if not fp.is_file():
        print(f"❌ 文件不存在: {fp}")
        sys.exit(1)

    # ---- 1. 上传 OSS ----
    object_name, public_url = _upload_oss(str(fp))

    # ---- 2. 提交异步转写 ----
    dashscope.api_key = DASHSCOPE_API_KEY
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

    print(f"📝 提交转写任务 ({MODEL}) ... ", end="", flush=True)
    task = Transcription.async_call(
        model=MODEL,
        file_urls=[public_url],
        language_hints=["zh", "en"],
    )
    task_id = task.output.task_id
    print(f"✓ task_id: {task_id}")

    # ---- 3. 轮询等待 ----
    print(f"⏳ 等待转写完成 ...", end="", flush=True)
    result = Transcription.wait(task=task_id)
    print(f" ✓ (status: {result.output.task_status})")

    if result.status_code != HTTPStatus.OK:
        print(f"❌ 转写失败: {result.output.message}")
        bucket.delete_object(object_name)
        sys.exit(1)

    # ---- 4. 下载结果 ----
    transcription_url = None
    for r in result.output.get("results", []):
        if r.get("subtask_status") == "SUCCEEDED":
            transcription_url = r.get("transcription_url")
            break

    if not transcription_url:
        print("❌ 未找到转写结果 URL")
        bucket.delete_object(object_name)
        sys.exit(1)

    print(f"📥 下载结果 ... ", end="", flush=True)
    raw_data = url_request.urlopen(transcription_url).read().decode("utf-8")
    data = json.loads(raw_data)
    print("✓")

    # ---- 5. 清理 OSS ----
    # 文件保留在 OSS，供其他模型复用
    # 手动跑 python3 cleanup_oss.py 统一清理

    # ---- 6. 保存 JSON ----
    json_path = fp.with_suffix(".transcript.json")
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"📄 JSON: {json_path}")

    # ---- 7. 保存纯文本 ----
    txt_path = fp.with_suffix(".transcript.txt")
    lines = []
    for transcript in data.get("transcripts", []):
        for sent in transcript.get("sentences", []):
            begin = sent["begin_time"] // 1000
            end = sent["end_time"] // 1000
            bts = f"{begin//3600:02d}:{(begin%3600)//60:02d}:{begin%60:02d}"
            ets = f"{end//3600:02d}:{(end%3600)//60:02d}:{end%60:02d}"
            lines.append(f"[{bts} - {ets}] {sent['text']}")
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 TXT : {txt_path}")

    # ---- 8. 统计 ----
    total_words = sum(
        len(w.get("text", ""))
        for t in data.get("transcripts", [])
        for s in t.get("sentences", [])
        for w in s.get("words", [])
    )
    total_sentences = sum(
        len(t.get("sentences", []))
        for t in data.get("transcripts", [])
    )
    print(f"\n📊 统计: {total_sentences} 句, ~{total_words} 词")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 transcribe.py <音视频文件>")
        sys.exit(1)
    transcribe_file(sys.argv[1])


if __name__ == "__main__":
    main()
