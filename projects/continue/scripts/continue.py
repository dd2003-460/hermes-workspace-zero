#!/usr/bin/env python3
"""
Continue Signal Hook — 通用 continue 信号注入脚本

用法（作为 shell hook 的 command）：
    python3 scripts/continue.py

输入（stdin JSON，由 hook 注入）：
    {
        "session_id": "xxx",
        "transcript_path": "/path/to/transcript.jsonl",
        "session_key": "platform:chat:thread",
        "next_prompt": "自动续写 prompt（可选，默认使用 continue_config）",
        "config": {
            "completion_promise": "<promise>",  // 完成条件，检测到则不继续
            "max_iterations": 10,               // 最大迭代次数
            "next_prompt_template": "继续分析..." // 每轮注入的 prompt
        }
    }

输出：
    写信号文件到 ~/.hermes/continue-signal-{session_key_hash}.txt
    如果完成条件达成或达到最大迭代次数，则不写入信号文件（停止循环）

信号文件内容由 gateway 读取并注入 _pending_messages
"""

import json
import sys
import os
import re
import hashlib
import time
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
SIGNAL_DIR = HERMES_DIR / "continue-signals"
SIGNAL_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "completion_promise": "<promise>",
    "max_iterations": 10,
    "next_prompt_template": "继续。检查当前进展并推进下一步。",
}


def get_session_key_hash(session_key: str) -> str:
    """生成 session_key 的短哈希，用于信号文件名"""
    return hashlib.md5(session_key.encode()).hexdigest()[:12]


def count_iterations(transcript_path: str) -> int:
    """从 transcript.jsonl 中计算已完成的 agent 迭代轮次"""
    if not transcript_path or not os.path.exists(transcript_path):
        return 0
    
    iteration_count = 0
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if 'agent:end' in line.lower():
                    iteration_count += 1
    except Exception as e:
        print(f"Warning: failed to parse transcript: {e}", file=sys.stderr)
    return iteration_count


def check_completion(transcript_path: str, completion_promise: str) -> bool:
    """检查完成条件：transcript 中是否包含 completion_promise"""
    if not transcript_path or not os.path.exists(transcript_path):
        return False
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查 transcript 中是否包含完成标志
        if completion_promise in content:
            print(f"Completion condition met: '{completion_promise}'", file=sys.stderr)
            return True
    except Exception as e:
        print(f"Warning: failed to check transcript: {e}", file=sys.stderr)
    
    return False


def write_signal_file(session_key: str, prompt: str):
    """写入 continue 信号文件，gateway 会读取并注入"""
    sig_hash = get_session_key_hash(session_key)
    signal_file = SIGNAL_DIR / f"signal-{sig_hash}.txt"
    
    # 写入信号（含时间戳避免旧信号重复触发）
    signal_content = f"{time.time()}:{prompt}"
    signal_file.write_text(signal_content, encoding='utf-8')
    
    print(f"Signal file written: {signal_file}", file=sys.stderr)
    print(f"Content length: {len(prompt)} chars", file=sys.stderr)
    
    return str(signal_file)


def main():
    try:
        # 读取 stdin JSON
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: failed to read stdin: {e}", file=sys.stderr)
        sys.exit(1)
    
    session_key = input_data.get("session_key", "")
    transcript_path = input_data.get("transcript_path", "")
    next_prompt = input_data.get("next_prompt", "")
    config = {**DEFAULT_CONFIG, **input_data.get("config", {})}
    
    completion_promise = config.get("completion_promise", DEFAULT_CONFIG["completion_promise"])
    max_iterations = config.get("max_iterations", DEFAULT_CONFIG["max_iterations"])
    next_prompt_template = config.get("next_prompt_template", DEFAULT_CONFIG["next_prompt_template"])
    
    # 检测完成条件
    if check_completion(transcript_path, completion_promise):
        print("Agent has completed. Stopping loop.", file=sys.stderr)
        # 清理旧信号文件
        sig_hash = get_session_key_hash(session_key)
        signal_file = SIGNAL_DIR / f"signal-{sig_hash}.txt"
        if signal_file.exists():
            signal_file.unlink()
        sys.exit(0)
    
    # 检查最大迭代次数
    current_iter = count_iterations(transcript_path)
    if current_iter >= max_iterations:
        print(f"Max iterations reached ({max_iterations}). Stopping loop.", file=sys.stderr)
        # 清理旧信号文件
        sig_hash = get_session_key_hash(session_key)
        signal_file = SIGNAL_DIR / f"signal-{sig_hash}.txt"
        if signal_file.exists():
            signal_file.unlink()
        sys.exit(0)
    
    print(f"Current iteration: {current_iter}/{max_iterations}", file=sys.stderr)
    
    # 生成下一个 prompt
    prompt = next_prompt if next_prompt else next_prompt_template
    print(f"Next prompt: {prompt[:100]}...", file=sys.stderr)
    
    # 写入信号文件
    signal_path = write_signal_file(session_key, prompt)
    
    # 输出确认信息
    result = {
        "status": "signal_written",
        "signal_file": signal_path,
        "iteration": current_iter + 1,
        "max_iterations": max_iterations,
        "next_prompt_length": len(prompt),
    }
    print(json.dumps(result), file=sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
