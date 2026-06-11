#!/usr/bin/env python3
"""TextBO-inspired Prompt Optimizer — persona-v3

灵感来源: TextBO (Kang & Yoganarasimhan)
扩展贝叶斯优化到语言空间，优化 prompt 文本以达到评估目标。

核心方法:
1. 将 persona-v3 prompt 视为优化变量
2. 用 unified_eval 评估作为目标函数
3. 通过关键词级修改 (add/remove/swap) 探索语言空间
4. 贪婪搜索找到评分最高的 prompt 变体

用法:
    python3 textbo_prompt_optimizer.py          # 运行优化
    python3 textbo_prompt_optimizer.py --dry-run # 仅显示候选修改
"""

import copy
import random
import sys
import subprocess
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROMPT_FILE = PROJECT_ROOT / "persona-v3-prompt.txt"
BASELINE_SCORE_FILE = PROJECT_ROOT / "eval_results" / "baseline_score.txt"

# 修改操作: 定义对 prompt 的可行变换
MODIFICATION_OPS = {
    "add_keyword": {
        "description": "添加关键词到目标维度",
        "params": [
            {"dim": "自适应感知", "keyword": "感知干扰", "weight": 1.0},
            {"dim": "自适应探索", "keyword": "探索深度", "weight": 1.0},
            {"dim": "自适应精度", "keyword": "精度层级", "weight": 1.0},
            {"dim": "自适应先验", "keyword": "后验分布", "weight": 1.0},
            {"dim": "自适应自我", "keyword": "观测者参数", "weight": 1.0},
            {"dim": "自适应投影", "keyword": "结构映射", "weight": 1.0},
        ]
    },
    "remove_keyword": {
        "description": "从过度饱和维度移除关键词",
        "params": [
            {"dim": "自适应精度", "keyword": "信噪比", "reason": "降低该维度得分以平衡"},
            {"dim": "自适应投影", "keyword": "低维", "reason": "过度跨维"},
        ]
    },
}


def load_prompt():
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding="utf-8")


def save_prompt(text, suffix=""):
    if suffix:
        path = PROJECT_ROOT / "persona-v3-prompt-tmp.txt"
    else:
        path = PROMPT_FILE
    path.write_text(text, encoding="utf-8")
    return path


def apply_modification(prompt, op_type, param):
    """应用单个修改到 prompt 文本。"""
    dim = param["dim"]
    keyword = param["keyword"]

    # 匹配 ### N. {dim} 或 ## {dim} 或 {dim} 独立行
    dim_header = f"### {dim}"
    dim_start = prompt.find(dim_header)
    if dim_start < 0:
        dim_header = f"## {dim}"
        dim_start = prompt.find(dim_header)
    if dim_start < 0:
        dim_header = f"### {dim}"  # try with number prefix
        dim_start = prompt.find(dim_header)
    if dim_start < 0:
        # 最后尝试: 按维度名称搜索
        for prefix in ["### 1.", "### 2.", "### 3.", "### 4.", "### 5.", "### 6."]:
            check = prefix + " " + dim
            dim_start = prompt.find(check)
            if dim_start >= 0:
                dim_header = check
                break

    if dim_start < 0:
        return prompt, None

    # 找到该维度内下一维度标题或文档结束
    next_dim = None
    for prefix in ["### 1.", "### 2.", "### 3.", "### 4.", "### 5.", "### 6."]:
        check_pos = prompt.find(prefix, dim_start + 3)
        if check_pos > dim_start and (next_dim is None or check_pos < next_dim):
            next_dim = check_pos

    if next_dim is None or next_dim < dim_start:
        dim_section = prompt[dim_start:]
    else:
        dim_section = prompt[dim_start:next_dim]

    kw_pattern = r"\*\*关键词\*\*: (.+)"
    kw_match = re.search(kw_pattern, dim_section)
    if not kw_match:
        return prompt, None

    original_keywords = kw_match.group(1).strip()
    full_start = dim_start + kw_match.start(1)
    full_end = dim_start + kw_match.end(1)

    if op_type == "add_keyword":
        if keyword not in original_keywords:
            new_keywords = f"{original_keywords}, {keyword}"
            new_prompt = prompt[:full_start] + new_keywords + prompt[full_end:]
            return new_prompt, f"添加 {keyword} 到 {dim}"
    elif op_type == "remove_keyword":
        if keyword in original_keywords:
            new_keywords = original_keywords.replace(f", {keyword}", "").replace(f"{keyword}, ", "").strip()
            if not new_keywords:
                new_keywords = original_keywords
            new_prompt = prompt[:full_start] + new_keywords + prompt[full_end:]
            return new_prompt, f"移除 {keyword} 从 {dim}"
    return prompt, None


def score_prompt(prompt_text):
    """通过保存修改后的 prompt 并运行 unified_eval 来评分。"""
    tmp_path = PROJECT_ROOT / "persona-v3-prompt-tmp.txt"
    tmp_path.write_text(prompt_text, encoding="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "unified_eval.py"), "--prompt"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
            timeout=60,
        )
        if result.returncode != 0:
            return None, f"eval error: {result.stderr[:100]}"

        # 解析输出
        scores = {}
        for line in result.stdout.split("\n"):
            if "平均" in line:
                m = re.search(r'平均\s+([\d.]+)', line)
                if m:
                    scores["avg"] = float(m.group(1))
            if "最小分" in line:
                m = re.search(r'最小[\s一-鿿]*分:?\s*([\d.]+)', line)
                if m:
                    scores["min"] = float(m.group(1))
            if "所有维度" in line and ">=" in line:
                if "True" in line:
                    scores["all_above"] = True
                elif "False" in line:
                    scores["all_above"] = False

        if "avg" in scores:
            return scores, None
        return None, f"无法解析输出: {result.stdout[:200]}"
    except subprocess.TimeoutExpired:
        return None, "timeout"
    finally:
        tmp_path.unlink(missing_ok=True)


def greedy_optimize(prompt, max_iterations=10, objective="avg"):
    """贪婪搜索: 每次迭代尝试所有修改，选择最好的。"""
    best_text = prompt
    best_score = score_prompt(prompt)
    if best_score[0] is None:
        raise RuntimeError(f"初始评分失败: {best_score[1]}")
    best_score_val = best_score[0][objective]

    print(f"初始评分: {best_score[0]}")
    print(f"优化目标: 最大化 {objective}")
    print()

    history = [{"iteration": 0, "score": best_score_val, "action": "baseline"}]

    for iteration in range(1, max_iterations + 1):
        improved = False
        candidates = []

        # 生成所有候选修改
        for op_type, op_config in MODIFICATION_OPS.items():
            for param in op_config["params"]:
                candidate_text, desc = apply_modification(best_text, op_type, param)
                if candidate_text != best_text and desc:
                    score, err = score_prompt(candidate_text)
                    if err is None and score and objective in score:
                        candidates.append({
                            "text": candidate_text,
                            "score": score,
                            "score_val": score[objective],
                            "action": f"{op_type}: {desc}",
                        })
                    # 清理 candidate 临时文件
                    tmp = PROJECT_ROOT / "persona-v3-prompt-tmp.txt"
                    if tmp.exists():
                        tmp.unlink(missing_ok=True)

        if not candidates:
            print(f"  迭代 {iteration}: 无有效候选")
            break

        # 选择最好的候选
        candidates.sort(key=lambda x: -x["score_val"])
        best_candidate = candidates[0]

        if best_candidate["score_val"] > best_score_val:
            # 采纳改进
            best_text = best_candidate["text"]
            best_score = (best_candidate["score"], None)
            best_score_val = best_candidate["score_val"]
            improved = True
            print(f"  迭代 {iteration}: 改进 ✓ — {best_candidate['action']}: {best_candidate['score']}")
            history.append({"iteration": iteration, "score": best_score_val, "action": best_candidate["action"]})
        else:
            print(f"  迭代 {iteration}: 无改进 (best candidate: {best_candidate['score_val']:.4f} vs current {best_score_val:.4f})")
            history.append({"iteration": iteration, "score": best_score_val, "action": "stagnant"})
            break

    # 恢复原始 prompt
    save_prompt(load_prompt(), suffix="")

    return {
        "best_score": best_score[0],
        "best_score_val": best_score_val,
        "baseline_score": score_prompt(PROMPT_FILE.read_text(encoding="utf-8"))[0][objective],
        "history": history,
        "improved": history[-1]["score"] > history[0]["score"],
    }


def main():
    print("=" * 60)
    print("TextBO-inspired Prompt Optimizer — persona-v3")
    print("基于贝叶斯优化的语言空间搜索")
    print("=" * 60)

    prompt = load_prompt()
    print(f"\nPrompt: {len(prompt)} chars, {len(prompt.split())} tokens")
    print(f"修改操作: {sum(len(v['params']) for v in MODIFICATION_OPS.values())} 个候选")
    print()

    # 尝试两种优化策略
    for objective, desc in [("avg", "平均评分"), ("min", "最小维度分")]:
        print(f"\n--- 优化策略: {desc} ({objective}) ---")
        result = greedy_optimize(prompt, max_iterations=5, objective=objective)
        if result["improved"]:
            print(f"\n✓ 在 {desc} 策略上找到改善!")
            break
        print(f"✗ {desc} 策略无改善")

    if not result.get("improved"):
        print(f"\n所有策略均未改善 — 提示词已接近最优")

    print(f"\n{'=' * 60}")
    print(f"优化结果: 改善={'是' if result['improved'] else '否'}")
    print(f"基线评分: {result['baseline_score']:.4f}")
    print(f"最佳评分: {result['best_score_val']:.4f}")
    print(f"提升: {result['best_score_val'] - result['baseline_score']:+.4f}")

    if result["history"][-1]["action"] != "stagnant":
        print(f"\n优化历史:")
        for h in result["history"]:
            print(f"  迭代 {h['iteration']}: score={h['score']:.4f} — {h['action']}")

    # Save report
    output_path = PROJECT_ROOT / "eval_results" / "textbo_optimization.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n报告保存: {output_path}")

    return 0


if __name__ == "__main__":
    main()
