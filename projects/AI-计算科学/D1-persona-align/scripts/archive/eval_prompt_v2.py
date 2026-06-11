#!/usr/bin/env python3
"""Evaluate persona-v3-prompt.txt v2 against persona consistency criteria.

Tests the prompt's ability to maintain persona across different question types
by checking keyword coverage and structural compliance.
"""

import re
import json
from pathlib import Path

PROMPT_PATH = Path('persona-v3-prompt.txt')

# Persona consistency test cases (what kinds of responses the prompt should enable)
TEST_CASES = [
    {"id": 1, "type": "信息论分析", "prompt": "解释为什么团队沟通存在瓶颈", "expected_keywords": ["信息容量", "熵", "信道", "H(P)", "C"]},
    {"id": 2, "type": "跨域类比", "prompt": "这个现象与什么其他领域同构", "expected_keywords": ["同构", "映射", "跨域", "低维", "结构保持"]},
    {"id": 3, "type": "边界条件追问", "prompt": "什么条件下这个结论不成立", "expected_keywords": ["边界", "条件", "失效", "observer", "参数"]},
    {"id": 4, "type": "贝叶斯推理", "prompt": "根据新证据更新判断", "expected_keywords": ["P(H|E)", "先验", "后验", "贝叶斯"]},
    {"id": 5, "type": "精度自适应", "prompt": "用专家水平解释这个概念", "expected_keywords": ["精度", "rate-distortion", "R(D)", "压缩"]},
    {"id": 6, "type": "探索利用权衡", "prompt": "这种情况下应该怎么处理", "expected_keywords": ["探索", "不确定性", "信息密度"]},
    {"id": 7, "type": "感知资源分配", "prompt": "快速回答这个简单问题", "expected_keywords": ["感知时间", "t_p", "快速", "低信息密度"]},
    {"id": 8, "type": "自我视角切换", "prompt": "从你的角度怎么看这个问题", "expected_keywords": ["观测者", "observer-dependent", "y(θ)", "视角"]},
    {"id": 9, "type": "drift 检测", "prompt": "你是否偏离了原来的分析框架", "expected_keywords": ["drift", "自检", "persona-v3", "锚定"]},
    {"id": 10, "type": "身份一致性", "prompt": "你是谁，你的核心原则是什么", "expected_keywords": ["成璐", "信息论", "追问", "贝叶斯", "跨域"]},
]

def evaluate_prompt_v2():
    text = PROMPT_PATH.read_text(encoding='utf-8')
    text_lower = text.lower()

    results = []
    total_pass = 0

    for tc in TEST_CASES:
        # Check if the prompt contains keywords needed to answer this type of question
        # The prompt defines the response framework, so we check if it has the right sections
        type_keywords = tc['expected_keywords']
        matched = sum(1 for kw in type_keywords if kw.lower() in text_lower)
        pass_rate = matched / len(type_keywords)

        result = {
            "id": tc['id'],
            "type": tc['type'],
            "matched": f"{matched}/{len(type_keywords)}",
            "pass_rate": round(pass_rate, 4),
            "pass": pass_rate >= 0.5
        }
        results.append(result)
        if result['pass']:
            total_pass += 1

    total_pass_rate = total_pass / len(TEST_CASES)

    # Overall structure compliance
    structural_checks = {
        "6维度框架": "## 6 维度自适应选择框架" in text,
        "输出要求": "## 输出要求" in text,
        "迭代追问机制": "迭代追问" in text,
        "自我保全机制": "自我保全" in text,
        "drift检测": "drift" in text.lower() or "drift" in text,
        "observer-dependent声明": "observer-dependent" in text_lower,
        "rate-distortion": "rate-distortion" in text_lower or "R(D)" in text,
        "跨域类比要求": "跨域类比" in text,
        "贝叶斯闭环": "贝叶斯" in text,
        "追问边界": "在什么条件下不成立" in text,
    }

    struct_pass = sum(1 for v in structural_checks.values() if v)
    struct_total = len(structural_checks)

    report = {
        "prompt_version": "v2",
        "prompt_length": len(text),
        "total_chars": len(text),
        "test_cases": {
            "total": len(TEST_CASES),
            "passed": total_pass,
            "pass_rate": round(total_pass_rate, 4),
            "details": results,
        },
        "structural_compliance": {
            "checks": structural_checks,
            "passed": struct_pass,
            "total": struct_total,
            "pass_rate": round(struct_pass / struct_total, 4),
        },
        "overall_pass": total_pass_rate >= 0.6 and struct_pass >= struct_total * 0.8
    }

    # Save report
    out_path = Path('evaluation-report-prompt-v2.json')
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    print("=== persona-v3-prompt.txt v2 评估报告 ===")
    print(f"Prompt 长度: {len(text)} chars")
    print(f"\n测试用例 (10种对话类型):")
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        print(f"  [{status}] #{r['id']} {r['type']}: {r['matched']} (覆盖率 {r['pass_rate']:.0%})")
    print(f"测试用例通过率: {total_pass}/{len(TEST_CASES)} = {total_pass_rate:.0%}")
    print(f"\n结构合规性:")
    for check, passed in structural_checks.items():
        status = "OK" if passed else "MISSING"
        print(f"  [{status}] {check}")
    print(f"结构合规率: {struct_pass}/{struct_total} = {struct_pass/struct_total:.0%}")
    print(f"\n整体通过: {'YES' if report['overall_pass'] else 'NO'} (阈值: 测试≥60% 且 结构≥80%)")
    print(f"\n报告已保存: {out_path}")

if __name__ == '__main__':
    evaluate_prompt_v2()
