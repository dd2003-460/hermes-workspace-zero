#!/usr/bin/env python3
# origin: ai
"""interruption_injector.py — 对AI生成文本注入"中断"模式，模拟成璐打字时的无意识中断。

三种中断模式（频率来自GT统计，单位：次/千字）：
  1. 括号插话 ~0.4：断言句（。/？结尾）后插入"（...）"自我觉察
  2. 编号跳跃 ~1.0：编号序列中随机跳过（2 → 2.2 / 3.1 这类子编号）
  3. 截断     ~0.5：随机一句话在中间截断（删掉尾部2-5个字符），下一句直接开始

用法：
  python3 interruption_injector.py --input <md文件> [--seed 42] [--dry-run] [--frequency-scale 1.0]

输出：
  {原文件名}-injected.md
  stdout：注入报告

只用标准库。不改变原文语义，只插入中断；保持markdown结构。
"""

import argparse
import os
import random
import re
import sys

# 预设括号插话池（成璐GT中观察到的自我觉察短语）
PAREN_PHRASES = [
    "（也许是因为我在的地方太垃圾？）",
    "（这是个局部，不客观的形容）",
    "（当然其实应该没有...这只是错觉）",
    "（我跑题了）",
    "（这个说法信度不高）",
    "（回头验证）",
    "（也许它就是要那种装精确的傲慢地感觉）",
]

# 频率（次/千字，GT统计）
FREQ_PAREN = 0.4
FREQ_JUMP = 1.0
FREQ_TRUNC = 0.5

# 编号行：行首 整数. 或 整数、（排除已存在的子编号如 1.1）
NUM_LINE_RE = re.compile(r"^(\s*)(\d+)([\.、])(?!\d)")
# 断言句结尾：全角句号/问号/叹号（排除小数点）
SENT_END_RE = re.compile(r"([。？！])")
# 编号/分隔符：编号+空格 或 编号+空格+中文（用于行内句子边界）
NUM_SEP_RE = re.compile(r"(\d+\.\s+[\u4e00-\u9fff]|\d+\s+[\u4e00-\u9fff]|Show more)")
# 代码块围栏
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def cjk_count(text):
    """统计CJK字数（不含markdown符号/英文）。"""
    n = 0
    in_fence = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        n += sum(1 for ch in line if "\u4e00" <= ch <= "\u9fff")
    return n


def split_sentences(text):
    """按行处理，返回句子片段列表 [(start, end, sentence_text)]。
    句子边界：。？！ 或 编号+空格（如 " 1." " 2.1" " Show more"）。
    跳过代码块内和标题行。
    """
    sents = []
    in_fence = False
    for line_start_offset, line in line_offsets(text):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith(("#", "|", ">", "-", "*")):
            continue
        abs_start = line_start_offset
        i = 0
        while i < len(line):
            m_punct = SENT_END_RE.search(line, i)
            m_num = NUM_SEP_RE.search(line, i) if i > 0 else None
            candidates = []
            if m_punct:
                candidates.append(m_punct.end())
            if m_num and m_num.start() > i:
                candidates.append(m_num.start())
            if not candidates:
                break
            end = min(candidates)
            seg = line[i:end]
            if len(seg) >= 6 and not seg.strip().startswith("（"):
                sents.append((abs_start + i, abs_start + end, seg))
            i = end
    return sents


def line_offsets(text):
    """返回 [(行在全文中的起始偏移, 行文本)]（行文本不含换行符）。"""
    out = []
    off = 0
    for line in text.split("\n"):
        out.append((off, line))
        off += len(line) + 1
    return out


def find_numbered_lines(text):
    """返回 [(行起始偏移, 数字int, 行文本)]，行首编号。"""
    out = []
    in_fence = False
    for off, line in line_offsets(text):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = NUM_LINE_RE.match(line)
        if m:
            out.append((off, int(m.group(2)), line))
    return out


def plan_injections(text, rng, scale):
    """计算三种注入的计划。返回 (plans, info)。
    plans: 列表，每项 (kind, offset_in_text, payload_or_desc)
    info: 统计dict
    """
    n = cjk_count(text)
    info = {
        "cjk": n,
        "n_paren_target": max(0, round(FREQ_PAREN * scale * n / 1000)),
        "n_jump_target": max(0, round(FREQ_JUMP * scale * n / 1000)),
        "n_trunc_target": max(0, round(FREQ_TRUNC * scale * n / 1000)),
    }
    plans = []

    # --- 括号插话 ---
    sents = split_sentences(text)
    # 候选：句末位置不在已有括号附近；排除句内已含"（"的（不插到已有括号处）
    paren_candidates = [s for s in sents if "（" not in s[2] and "）" not in s[2]]
    rng.shuffle(paren_candidates)
    # 位置去重：同一处不重复插
    used_positions = set()
    for (s, e, seg) in paren_candidates:
        if len(plans) >= info["n_paren_target"]:
            break
        if any(abs(e - (p[1])) < 12 for p in plans):
            continue
        phrase = rng.choice(PAREN_PHRASES)
        plans.append(("paren", e, phrase))
        used_positions.add(e)

    # --- 编号跳跃 ---
    nums = find_numbered_lines(text)
    if nums and info["n_jump_target"] > 0:
        # 只跳「序列中间」的编号：前后都存在更大/更小的编号（跳过首尾，
        # 孤立编号不跳，避免产生无来由的子编号）
        values = [n for (_, n, _) in nums]
        for idx, (off, num, line) in enumerate(nums):
            if num not in values[:idx] and num not in values[idx+1:]:
                continue
        jumpable = []
        for idx, (off, num, line) in enumerate(nums):
            prev_has = any(v != num for (o, v, l) in nums[:idx])
            next_has = any(v != num for (o, v, l) in nums[idx+1:])
            if prev_has and next_has:
                jumpable.append((off, num, line))
        rng.shuffle(jumpable)
        suffix_pool = ["2", "3", "1", "5"]
        for (off, num, line) in jumpable:
            if len([p for p in plans if p[0] == "jump"]) >= info["n_jump_target"]:
                break
            new_num = f"{num}.{rng.choice(suffix_pool)}"
            plans.append(("jump", off, f"{num}→{new_num}"))

    # --- 截断 ---
    trunc_candidates = [s for s in sents if len(s[2]) >= 8]
    rng.shuffle(trunc_candidates)
    for (s, e, seg) in trunc_candidates:
        if len([p for p in plans if p[0] == "trunc"]) >= info["n_trunc_target"]:
            break
        # 不与已有计划位置冲突
        if any(abs(e - p[1]) < 12 for p in plans):
            continue
        # 截断：删掉句子末尾（句号前）的2-5个字，保留句号
        body = seg.rstrip("。？！")
        if len(body) < 8:
            continue
        cut = rng.randint(2, 5)
        if cut >= len(body) - 4:
            cut = max(2, len(body) // 2)
        # 保护：截断后句尾不能只剩标点（避免"，。"这类病句）
        while cut < len(body) and body[len(body) - cut - 1].strip("。？！，、；：") == "":
            cut += 1
        truncated = body[: len(body) - cut]
        new_seg = truncated + "。"
        plans.append(("trunc", s, new_seg))

    return plans, info


def apply_plans(text, plans):
    """按计划修改文本（offset均基于原文）。返回新文本+应用明细。
    从后往前应用避免偏移失效。
    """
    applied = []
    # 排序：offset降序；同offset的按kind
    for kind, off, payload in sorted(plans, key=lambda p: -p[1]):
        if kind == "paren":
            text = text[:off] + payload + text[off:]
            applied.append((kind, off, payload))
        elif kind == "trunc":
            # payload是新句；需要知道原句长度——用记录的原跨度
            # 这里简化：trunc plan的payload是元组(新句, 原句长)
            new_seg, old_len = payload
            text = text[:off] + new_seg + text[off + old_len:]
            applied.append((kind, off, new_seg))
        elif kind == "jump":
            # 替换行首编号（payload格式 "old→new"）
            old_num, new_num = payload.split("→")
            m = NUM_LINE_RE.match(text[off:])
            if m:
                text = text[: off + m.start(2)] + new_num + text[off + m.end(2):]
                applied.append((kind, off, payload))
    return text, applied


def main():
    ap = argparse.ArgumentParser(description="对AI文本注入成璐式中断模式")
    ap.add_argument("--input", required=True, help="输入markdown文件路径")
    ap.add_argument("--seed", type=int, default=42, help="随机种子，默认42")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不写文件")
    ap.add_argument("--frequency-scale", type=float, default=1.0, help="频率缩放，默认1.0")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    rng = random.Random(args.seed)
    plans, info = plan_injections(text, rng, args.frequency_scale)

    # 截断计划需要带原句长度——重新计算
    for i, (kind, off, payload) in enumerate(plans):
        if kind == "trunc":
            # 找原句：从off开始到下一个句末
            m = SENT_END_RE.search(text, off)
            if m:
                old_len = m.end() - off
                plans[i] = ("trunc", off, (payload, old_len))

    n_p = sum(1 for p in plans if p[0] == "paren")
    n_j = sum(1 for p in plans if p[0] == "jump")
    n_t = sum(1 for p in plans if p[0] == "trunc")

    print(f"=== 中断注入报告 ===")
    print(f"输入: {args.input}")
    print(f"CJK字数: {info['cjk']}")
    print(f"频率scale: {args.frequency_scale}  seed: {args.seed}")
    print(f"目标: 括号{info['n_paren_target']} 跳号{info['n_jump_target']} 截断{info['n_trunc_target']}")
    print(f"实际: 括号{n_p} 跳号{n_j} 截断{n_t}")
    print()
    for kind, off, payload in sorted(plans, key=lambda p: p[1]):
        ctx_start = max(0, off - 10)
        ctx = text[ctx_start:off].replace("\n", "⏎")
        if kind == "paren":
            print(f"  [括号] @{off} ...{ctx}｜→ {payload}")
        elif kind == "jump":
            # payload格式 "old→new"
            old_num, new_num = payload.split("→")
            print(f"  [跳号] @{off} 编号{old_num} → {new_num}")
        elif kind == "trunc":
            new_seg, old_len = payload
            print(f"  [截断] @{off} 「{text[off:off+old_len]}」 → 「{new_seg}」")

    if args.dry_run:
        print("\n[dry-run] 未修改任何文件。")
        return

    out_path = args.input[:-3] + "-injected.md" if args.input.endswith(".md") else args.input + "-injected"
    new_text, applied = apply_plans(text, plans)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"\n已写入: {out_path}")


if __name__ == "__main__":
    main()
