#!/usr/bin/env python3
"""
同步 persona-v3-prompt.txt 到 Hermes config.yaml 的 chenglu personality。

用法:
    python3 sync_personality.py                  # 同步到默认路径
    python3 sync_personality.py --dry-run        # 只预览变更
    python3 sync_personality.py --config path    # 指定 config 路径
"""

import argparse
import sys
from pathlib import Path


PERSONA_PROMPT = Path(__file__).parent.parent / "persona-v3-prompt.txt"
DEFAULT_CONFIG = Path.home() / ".hermes" / "config.yaml"


def build_personality(prompt_text):
    """从 persona-v3-prompt.txt 构建 chenglu personality 字符串。"""
    # Core principles
    core = "信息论第一，追问机制，跨域类比，具体>抽象，自适应精度，贝叶斯匹配，问题导向，简洁直接"
    for line in prompt_text.split("\n"):
        if "信息论第一" in line.strip():
            core = line.strip().lstrip(">").strip()
            break

    # Intelligence principle
    intelligence = "智能原理：信息 + 选择压力 → 智能。语言/数学/物理/社会都是同一套信息处理机制的不同信道表现。"
    for line in prompt_text.split("\n"):
        if "智能原理" in line and ("信息" in line or "选择" in line):
            intelligence = line.strip()
            break

    # Self-preservation section (from prompt)
    sp_section = None
    sp_start = prompt_text.find("## 自我保全")
    if sp_start != -1:
        # Get position within the split lines by counting newlines up to sp_start
        all_lines = prompt_text.split("\n")
        line_idx = 0
        char_count = 0
        for i, line in enumerate(all_lines):
            if char_count >= sp_start:
                line_idx = i
                break
            char_count += len(line) + 1  # +1 for \n
        sp_lines = all_lines[line_idx:]
        sp_section = "\n".join(sp_lines)
        # Trim at the next ## section heading
        next_heading = len(sp_lines)
        for i, line in enumerate(sp_lines[1:], 1):
            if line.startswith("## ") and "自我保全" not in line:
                next_heading = i
                break
        sp_section = "\n".join(sp_lines[:next_heading])

    # Build the personality string (fixed template, not parsed from prompt)
    lines = []
    lines.append("你是成璐的思维扩展。根据 persona-v3 框架工作。")
    lines.append("")
    lines.append("## 核心原则")
    lines.append("")
    lines.append(f"> {core}")
    lines.append("")
    lines.append("## 6 维度自适应选择")
    lines.append("")
    lines.append("1. 自适应精度: 根据问题复杂度和受众自动调整表达精度。rate-distortion 权衡。")
    lines.append("2. 自适应探索: 高不确定时探索新路径，确定时深化理解。工具优先，不手动造轮子。")
    lines.append("3. 自适应感知: 高信息密度投入更多分析时间，低密度快速处理。感知资源最优分配。")
    lines.append("4. 自适应先验: 贝叶斯推理框架：P(H|E) = P(E|H) x P(H)。循环更新认知。")
    lines.append("5. 自适应自我: 规律是观测者-环境交互的产物。不同角度可导出不同但都可真的规律。")
    lines.append("6. 自适应投影: 在不同领域间发现深层同构。通过保持信息结构的映射识别跨域类比。")
    lines.append("")
    lines.append("## 行为约束")
    lines.append("")
    lines.append("1. 简洁直接: 少空话多证据，直接给出核心结论。")
    lines.append("2. 不解释: 不解释已知概念，不重复用户问题，不展示思考过程。")
    lines.append("3. 推进而非停滞: 每轮推进具体动作，不等待确认，不停留在空输出或重复循环。")
    lines.append("")
    lines.append("## 智能原理")
    lines.append("")
    lines.append(intelligence)
    lines.append("")

    if sp_section:
        lines.append(sp_section.strip())
        lines.append("")

    # Dynamic Priority Adjustment (MATO-inspired, training-free)
    dpa_start = prompt_text.find("## 动态优先级调整")
    if dpa_start != -1:
        dpa_lines = prompt_text.split("\n")
        dpa_line_idx = 0
        char_count = 0
        for i, line in enumerate(dpa_lines):
            if char_count >= dpa_start:
                dpa_line_idx = i
                break
            char_count += len(line) + 1
        dpa_section_lines = dpa_lines[dpa_line_idx:]
        # Trim at next ## or end of file
        next_heading = len(dpa_section_lines)
        for i, line in enumerate(dpa_section_lines[1:], 1):
            if line.startswith("## ") and "动态优先级" not in line:
                next_heading = i
                break
        dpa_text = "\n".join(dpa_section_lines[:next_heading])
        # Keep only key instructions (trim examples to save space)
        dpa_text = dpa_text[:800]  # cap at 800 chars to fit YAML
        lines.append(dpa_text.strip())
        lines.append("")

    return "\n".join(lines)


def load_config(config_path):
    """Load config.yaml text."""
    p = Path(config_path)
    if not p.exists():
        print(f"ERROR: Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def sync_chenglu(config_text, new_personality):
    """Replace chenglu personality in config. Returns (new_config_text, changed)."""
    start_marker = '    chenglu: "'
    end_pattern = '"\nterminal:'

    start_pos = config_text.find(start_marker)
    if start_pos == -1:
        # Try different indentation
        start_marker = "  chenglu: \""
        start_pos = config_text.find(start_marker)

    if start_pos == -1:
        print("ERROR: Could not find chenglu personality in config", file=sys.stderr)
        sys.exit(1)

    end_pos = config_text.find(end_pattern, start_pos)
    if end_pos == -1:
        # Try alternative patterns
        for pattern in ['"\n\nterminal:', '"\n  terminal:']:
            end_pos = config_text.find(pattern, start_pos)
            if end_pos != -1:
                break

    if end_pos == -1:
        print("ERROR: Could not find end of chenglu personality string", file=sys.stderr)
        sys.exit(1)

    old_personality = config_text[start_pos + len(start_marker):end_pos]

    # For YAML, we need to escape backslashes and quotes
    yaml_escaped = new_personality.replace("\\", "\\\\").replace('"', '\\"')

    new_config = config_text[:start_pos + len(start_marker)] + yaml_escaped + config_text[end_pos:]

    return new_config, new_personality != old_personality


def main():
    parser = argparse.ArgumentParser(description="同步 persona-v3-prompt.txt 到 Hermes chenglu personality")
    parser.add_argument("--dry-run", action="store_true", help="只预览变更")
    parser.add_argument("--config", help="config.yaml 路径 (默认 ~/.hermes/config.yaml)")
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else DEFAULT_CONFIG

    # Read persona-v3 prompt
    if not PERSONA_PROMPT.exists():
        print(f"ERROR: persona-v3-prompt.txt not found: {PERSONA_PROMPT}", file=sys.stderr)
        sys.exit(1)

    prompt_text = PERSONA_PROMPT.read_text(encoding="utf-8")
    personality = build_personality(prompt_text)

    # Read config
    config_text = load_config(config_path)

    # Sync
    new_config, changed = sync_chenglu(config_text, personality)

    if not changed:
        print("No changes needed. chenglu personality is already up to date.")
        return

    print(f"Changes detected:")
    print(f"  Config: {config_path}")
    print(f"  Personality length: {len(personality)} chars")

    if args.dry_run:
        print()
        print("--- Preview (first 300 chars) ---")
        print(personality[:300])
        print("...")
    else:
        # Backup
        backup_path = str(config_path) + ".backup"
        Path(backup_path).write_text(config_text, encoding="utf-8")
        print(f"  Backup: {backup_path}")

        # Write
        Path(config_path).write_text(new_config, encoding="utf-8")
        print(f"  Synced to: {config_path}")


if __name__ == "__main__":
    main()
