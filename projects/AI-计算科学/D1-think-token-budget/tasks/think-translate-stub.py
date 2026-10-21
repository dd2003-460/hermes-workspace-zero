#!/usr/bin/env python3
"""think-translate stub: 最小可运行的 THINK_TRANSLATE_CMD 翻译子进程。
协议: stdin JSONL 请求 {"id":"...","part":"英文"}  →  stdout 行响应 "id:中文"（每请求一行）
当前用 echo 式伪翻译（[中文]前缀），替换 translate() 即可接入真模型。
用法: THINK_TRANSLATE_CMD="python3 /path/to/think-translate-stub.py"
"""
import json
import sys


def translate(part: str) -> str:
    # 注: out 里不要含换行（行协议按 \n 分隔）；真实 NMT 输出后做 out.replace("\n", " ")
    # TODO: 替换为真实 NMT，例如:
    #   - argostranslate 包:  import argostranslate.package; ... package.install(); argostranslate.translate.translate(part, 'en', 'zh')
    #   - onnxruntime + NLLB-600M-distilled:  加载 model.onnx，tokenizer 分词，en→zh 推理
    return "[中文] " + part


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            rid = msg["id"]
            out = translate(msg["part"])
        except Exception as e:
            # 任何错误都回传原文，保证 thinking 不丢
            sys.stderr.write(f"translate error: {e}\n")
            continue
        # 行协议: "id:out"（proxy 端 translatePushLine 按首个冒号拆分）
        sys.stdout.write(f"{rid}:{out}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
