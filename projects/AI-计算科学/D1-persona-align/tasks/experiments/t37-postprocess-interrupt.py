#!/usr/bin/env python3
"""T37: 后处理中断注入脚本

功能：对 AI 生成的文本注入成璐的中断特征（括号插话/编号跳跃/截断），频率从 GT 统计。

GT 频率（t36-gt-samples.json, 7423 字）：
- 括号插话: 4.6/1000 字
- 编号跳跃: 2.7/1000 字
- 截断: 9 处/7423 字 ≈ 1.2/1000 字

用法：
    python3 t37-postprocess-interrupt.py <input.txt> [output.txt]

输入：AI 生成的纯文本（一整段，不换行）
输出：注入中断特征后的文本
"""
import random
import re
import sys
from pathlib import Path

# GT 统计的频率（每 1000 字）
PAREN_FREQ = 4.6
NUMBER_JUMP_FREQ = 2.7
TRUNCATION_FREQ = 1.2

# 括号插话模板（成璐风格）
PAREN_TEMPLATES = [
    "（也许是因为我在的地方太垃圾？）",
    "（尽管我不是）",
    "（你是谁）",
    "（这是局部，不客观的形容）",
    "（仅两个样本的联想）",
    "（我傲慢地感觉）",
    "（我猜）",
    "（信度不高）",
    "（我没法证明）",
    "（也许你有别的看法）",
    "（但我也说不准）",
    "（这是个根本限制）",
]

# 编号跳跃策略：在现有编号中随机跳号
def inject_number_jumps(text: str) -> str:
    """注入编号跳跃（1.2后面可能是2.2，中间跳过2和2.1）"""
    # 找到所有编号
    numbers = re.findall(r'(\d+)\.(\d+)', text)
    if len(numbers) < 2:
        return text

    # 随机选择一些位置进行跳号
    for i in range(len(numbers) - 1):
        if random.random() < 0.3:  # 30% 概率跳号
            current_minor = int(numbers[i][1])
            next_minor = int(numbers[i + 1][1])
            if next_minor - current_minor == 1:
                # 插入一个跳号
                skip = current_minor + random.randint(2, 3)
                replacement = f"{numbers[i][0]}.{skip}"
                text = text.replace(f"{numbers[i + 1][0]}.{numbers[i + 1][1]}", replacement, 1)

    return text


def inject_paren_insertions(text: str) -> str:
    """注入括号插话（自我觉察/质疑/中断）"""
    # 将文本分成句子
    sentences = re.split(r'(?<=[。！？])|(?<=\.)', text)

    inserted = 0
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue
        # 按频率决定注入
        if random.random() < (PAREN_FREQ / 1000) * len(sentence):
            # 随机选择位置插入
            pos = random.randint(0, len(sentence))
            template = random.choice(PAREN_TEMPLATES)
            sentences[i] = sentence[:pos] + template + sentence[pos:]
            inserted += 1

    return ''.join(sentences)


def inject_truncations(text: str) -> str:
    """注入截断（一句话没说完就停）"""
    # 找到句子边界
    sentences = re.split(r'(?<=[。！？])|(?<=\.)', text)

    truncated = 0
    for i, sentence in enumerate(sentences):
        if not sentence.strip() or len(sentence) < 20:
            continue
        # 按频率决定截断
        if random.random() < (TRUNCATION_FREQ / 1000) * len(sentence):
            # 随机截断（保留前 50-80%）
            cut_pos = int(len(sentence) * random.uniform(0.5, 0.8))
            sentences[i] = sentence[:cut_pos] + '...'
            truncated += 1

    return ''.join(sentences)


def postprocess(text: str) -> str:
    """应用所有后处理中断注入"""
    # 顺序：编号跳跃 → 括号插话 → 截断
    text = inject_number_jumps(text)
    text = inject_paren_insertions(text)
    text = inject_truncations(text)
    return text


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.txt> [output.txt]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix('.interrupted.txt')

    text = input_path.read_text()
    processed = postprocess(text)

    output_path.write_text(processed)
    print(f"Input: {len(text)} chars")
    print(f"Output: {len(processed)} chars")
    print(f"Saved to {output_path}")


if __name__ == '__main__':
    random.seed(42)  # 可复现
    main()
