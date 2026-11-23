"""机械退化循环检测器（repetition degeneration detector）。
检测目标：LLM 输出中"重复块循环 + 无最终答案块"的确定性退化路径。
在 T-PUB-1 Q04 五条已知路径上验证：r3/r5（循环）应判退化，r1/r2/r4（正常）应判正常。
"""
import json, re, sys

def detect_degeneration(text, min_repeat_len=40, min_repeat_count=3,
                        answer_patterns=(r'Answer:', r'\\boxed', r'最终', r'结论', r'答案：', r'Final Answer')):
    """返回 {degenerated: bool, repeat_len: int, repeat_count: int, has_answer: bool, score: float}
    score = 退化置信度 0-1（重复块长度 × 重复次数 / 文本长度 的归一化）。
    """
    # 1) 找最长连续重复块（chunk 紧接自身）
    best_len, best_count = 0, 0
    # 用滑窗找重复：对每个起始位置 i 和长度 L，检查 s[i:i+L] == s[i+L:i+2L]
    # 优化：只检查 L 是 min_repeat_len 的倍数，步长 20
    n = len(text)
    for L in range(min_repeat_len, min(min_repeat_len + 360, n // 3), 10):
        for i in range(0, max(1, n - 2 * L), 10):
            chunk = text[i:i+L]
            if text[i+L:i+2*L] == chunk:
                # 数连续重复次数
                cnt = 1
                pos = i + L
                while text[pos:pos+L] == chunk and pos + L <= n:
                    cnt += 1
                    pos += L
                if L > best_len:
                    best_len, best_count = L, cnt
                elif L == best_len and cnt > best_count:
                    best_count = cnt
                break  # 同长度找到一个就够

    # 2) 检测答案块
    has_answer = any(re.search(p, text) for p in answer_patterns)

    # 3) 退化判定：重复块 ≥ min_repeat_len 且重复 ≥ min_repeat_count 且无答案块
    degenerated = (best_len >= min_repeat_len and best_count >= min_repeat_count and not has_answer)

    # 4) 退化置信度
    if n == 0:
        score = 0.0
    else:
        score = min(1.0, (best_len * best_count) / (n * 0.3))

    return {
        "degenerated": degenerated,
        "repeat_len": best_len,
        "repeat_count": best_count,
        "has_answer": has_answer,
        "score": round(score, 3),
    }

if __name__ == "__main__":
    d = json.load(open("/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-generalization/tasks/T-PUB-1/full7-mt12000.json"))
    print("=== Q04 mt12000 五条路径退化检测 ===")
    print(f"{'run':<6}{'len':<8}{'degen':<8}{'rep_len':<10}{'rep_cnt':<9}{'ans':<6}{'score':<8}{'actual'}")
    correct = 0
    for i in range(1, 6):
        k = f"Q04/mt12000/r{i}"
        out = d[k]["out"]
        score = sum(d[k]["r"].values())
        r = detect_degeneration(out)
        # ground truth: score < 5 = 退化路径
        gt_degen = score < 5
        match = "✓" if r["degenerated"] == gt_degen else "✗"
        if r["degenerated"] == gt_degen:
            correct += 1
        print(f"r{i:<5}{len(out):<8}{str(r['degenerated']):<8}{r['repeat_len']:<10}{r['repeat_count']:<9}{str(r['has_answer']):<6}{r['score']:<8}{score}/5 {match}")
    print(f"\n检测准确率: {correct}/5")
    # 阈值敏感性
    print("\n=== 阈值敏感性（min_repeat_count）===")
    for mrc in [2, 3, 4, 5]:
        results = []
        for i in range(1, 6):
            out = d[f"Q04/mt12000/r{i}"]["out"]
            score = sum(d[f"Q04/mt12000/r{i}"]["r"].values())
            r = detect_degeneration(out, min_repeat_count=mrc)
            results.append((r["degenerated"], score < 5))
        acc = sum(1 for a, b in results if a == b) / len(results)
        print(f"  min_repeat_count={mrc}: acc={acc:.0%}")
