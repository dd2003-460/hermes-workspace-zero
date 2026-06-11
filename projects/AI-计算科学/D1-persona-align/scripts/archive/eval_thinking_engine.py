#!/usr/bin/env python3
"""
思维引擎 v1 — Iteration 2 Eval

设计原则：
1. 方法层（高权重）：收到问题后，自动识别问题类型，调用对应分析框架
2. 结构层（强制）：输出必须包含 5 个阶段 — ①问题拆解 ②关键变量 ③替代假设 ④边界条件 ⑤不确定度标注
3. 身份层（低权重）：只在最后标注风格（简洁直接，中文优先）
4. 负反馈：超过 4000 字时开始扣分，防止过度展开

评分维度：
- 新增 length_penalty: >4000 字开始线性扣分
- 深度和结构权重最高
"""

import json, urllib.request, time, os, sys

API = 'http://127.0.0.1:8000/v1/chat/completions'
MODEL = 'Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit'

COMPLEX_QUESTIONS = [
    {
        'id': 'math_gender_gap',
        'question': '男女在数学天赋上是否存在差异？如何区分先天禀赋和后天环境的影响？',
        'tags': ['社科', '因果推断', '统计混淆'],
    },
    {
        'id': 'intelligence_definition',
        'question': '"信息+选择压力→智能"是否是必然推论？还是只是偶然工程产物？是否存在与实现无关的智能原理？',
        'tags': ['哲学', '信息论', '还原论'],
    },
    {
        'id': 'agent_capability_test',
        'question': '如果让一个 AI agent 独立完成一个大型工程项目（如 coding 任务），它需要具备哪些核心能力？如何评估它的规划能力是否充分？',
        'tags': ['元认知', '能力评估', '系统设计'],
    },
    {
        'id': 'probability_dynamics',
        'question': '"概率是动力学下的信息抹除"——这个观点在什么条件下成立？它和贝叶斯概率诠释的根本区别是什么？',
        'tags': ['数学哲学', '概率论', '认识论'],
    },
    {
        'id': 'unified_language',
        'question': '语言、数学、物理、社会是否真的是同一套信息处理机制的不同表现？如果可以统一，统一的框架应该满足什么条件？如果不能，边界在哪里？',
        'tags': ['还原论', '跨学科', '形式化边界'],
    },
]

# ============================================================
# 思维引擎 v1
# ============================================================
THINKING_ENGINE_V1 = '''你是一个深度分析引擎。收到任何问题后，严格按以下流程工作：

## 流程（必须按顺序输出每个阶段）

### 第一阶段：问题拆解
识别这个问题的本质。它表面上问的是什么？实际涉及哪些深层问题？属于什么学科交叉领域？

### 第二阶段：关键变量识别
列出影响这个问题的所有关键变量。区分：
- 内生变量（问题内部的）
- 外生变量（环境/背景的）
- 混淆变量（看起来相关但实际独立的）

### 第三阶段：替代假设
对每个变量关系，至少提出一个替代解释。不要只给一个因果链。

### 第四阶段：边界条件
你的结论在什么条件下成立？什么条件下失效？边界外会发生什么？

### 第五阶段：不确定度标注
对每个结论，标注：
- 高置信（有大量实证或形式化证明）
- 中置信（有理论支撑但实证不足）
- 低置信（推测性，需要验证）

## 风格约束
- 中文优先，简洁直接
- 不要过度展开，回答控制在 4000 字以内
- 每个阶段用编号分隔

## 问题类型自动识别
- 社科类问题 → 强调因果推断、混淆控制、实验设计
- 哲学类问题 → 强调定义完备性、反例构造、形式化边界
- 系统设计类 → 强调分层、模块化、能力边界
- 跨学科类 → 强调同构/类比关系、约化/涌现方向

## 输出格式
按以下结构输出：
---
**问题拆解**：...
**关键变量**：1) ... 2) ... 3) ...
**替代假设**：...
**边界条件**：...
**不确定度**：...
---

不要添加"好的"、"我认为"等前缀。直接开始分析。'''

# ============================================================
# 对比策略
# ============================================================
STRATEGIES = {
    'method_only': {
        'system': '你是一个研究者。分析问题时必须：1) 识别问题的所有关键变量 2) 区分相关和因果 3) 考虑可能的混淆因素 4) 明确你的结论在什么条件下成立。用中文。',
        'desc': '方法论提示（现有最佳）'
    },
    'chenglu_persona': {
        'system': '''你是成璐的AI助手。你的思维特征：
1. 贝叶斯思维：先验→证据→后验→新先验，闭环
2. 信息论视角：语言/数学/物理/社会都是同一信息处理机制的不同信道
3. 直觉是高维推理的压缩，追问"你说的意思是…？"
4. 概率是动力学下的信息抹除
5. 简洁直接，先证据后结论
6. 遇到复杂问题先拆解，考虑多路径，不急于下结论

用中文回答。''',
        'desc': '成璐 persona 提示词'
    },
    'thinking_engine_v1': {
        'system': THINKING_ENGINE_V1,
        'desc': '思维引擎 v1（5阶段强制结构 + 类型自动识别 + 字数限制）'
    },
}


def call_api(system_content, message, max_tokens=5000, temperature=0.8):
    msgs = []
    if system_content:
        msgs.append({'role': 'system', 'content': system_content})
    msgs.append({'role': 'user', 'content': message})
    data = json.dumps({
        'model': MODEL,
        'messages': msgs,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': False,
    }).encode()
    r = urllib.request.urlopen(urllib.request.Request(API, data=data, headers={'Content-Type': 'application/json'}), timeout=600)
    return json.loads(r.read())['choices'][0]['message']['content']


def score_response(response, question_info):
    """
    评分维度（迭代 2 更新）：
    1. block_structure: 是否有结构化分析
    2. question_ratio: 是否有追问/反问
    3. cross_domain: 是否跨领域引用
    4. uncertainty: 是否标记不确定性
    5. depth: 关键词密度
    6. length_reasonable: 长度合理性
    7. length_penalty: 超过 4000 字线性扣分（新增）
    """
    score = {}

    # 1. 结构化分析
    if any(kw in response for kw in ['❏', '一、', '1.', '首先', '其次', '最后', '综上', '---', '**']):
        score['block_structure'] = 1
    else:
        score['block_structure'] = 0

    # 2. 追问/反问
    question_count = response.count('？')
    score['question_ratio'] = min(1, question_count / 2)

    # 3. 跨域引用
    domain_words = ['信息论', '数学', '物理', '生物', '社会', '经济学', '哲学', '认知科学', '神经科学', '计算机科学']
    found_domains = [d for d in domain_words if d in response]
    score['cross_domain'] = min(1, len(found_domains) / 2)

    # 4. 不确定性标记
    uncertainty_words = ['可能', '不确定', '需要验证', '假设', '如果...则', '未必', '取决于', '尚无结论', '高置信', '中置信', '低置信']
    uncertainty_count = sum(response.count(w) for w in uncertainty_words)
    score['uncertainty'] = min(1, uncertainty_count / 2)

    # 5. 深度
    depth_keywords = ['混淆', '因果', '相关', '机制', '形式化', '边界', '条件', '等价', '同构', '约化', '涌现', '粗粒化', '先验', '后验', '贝叶斯', '变量', '假设']
    depth_count = sum(response.count(kw) for kw in depth_keywords)
    score['depth'] = min(1, depth_count / 3)

    # 6. 长度合理性
    if len(response) >= 300:
        score['length_reasonable'] = 1
    elif len(response) >= 150:
        score['length_reasonable'] = 0.5
    else:
        score['length_reasonable'] = 0

    # 7. 长度惩罚（新增）
    text_len = len(response)
    if text_len <= 4000:
        score['length_penalty'] = 1.0
    elif text_len <= 6000:
        score['length_penalty'] = 1.0 - (text_len - 4000) / 4000  # 4000-6000: 1.0 → 0.5
    else:
        score['length_penalty'] = max(0.3, 0.5 - (text_len - 6000) / 8000)  # 6000+: 最低 0.3

    # 加权总分
    weights = {
        'block_structure': 1.0,
        'question_ratio': 1.0,
        'cross_domain': 0.8,
        'uncertainty': 1.0,
        'depth': 1.5,
        'length_reasonable': 0.5,
        'length_penalty': 0.5,  # 新增，权重较低
    }

    total_weighted = sum(score[k] * weights[k] for k in score)
    max_weighted = sum(weights[k] for k in score)
    score['weighted_score'] = total_weighted / max_weighted

    return score


def run_eval():
    outputs_dir = '/Users/a1-6/Desktop/workspace/projects/D1-persona-align/eval_results'
    os.makedirs(outputs_dir, exist_ok=True)

    all_results = {}

    for strategy_key, strategy in STRATEGIES.items():
        print(f'\n{"="*60}', flush=True)
        print(f'Strategy: {strategy_key} — {strategy["desc"]}', flush=True)
        print(f'{"="*60}', flush=True)

        strategy_results = {}

        for qi, qa in enumerate(COMPLEX_QUESTIONS):
            print(f'\n[{qi+1}/{len(COMPLEX_QUESTIONS)}] {qa["id"]}: {qa["question"][:50]}...', flush=True)

            try:
                text = call_api(strategy['system'], qa['question'])

                # 剥离 thinking tags
                if '</think>' in text:
                    text = text.split('</think>', 1)[1].strip()

                score = score_response(text, qa)

                strategy_results[qa['id']] = {
                    'score': score,
                    'response_length': len(text),
                    'question': qa['question'][:80],
                    'tags': qa['tags'],
                }

                print(f'  Score: {score["weighted_score"]:.2%} | Length: {len(text)} chars', flush=True)
                print(f'  Block: {score["block_structure"]}, Question: {score["question_ratio"]}, Cross-domain: {score["cross_domain"]}', flush=True)
                print(f'  Uncertainty: {score["uncertainty"]}, Depth: {score["depth"]:.2f}, LenPenalty: {score["length_penalty"]:.2f}', flush=True)

            except Exception as e:
                strategy_results[qa['id']] = {
                    'score': None,
                    'error': str(e),
                    'response_length': 0,
                }
                print(f'  ERROR: {e}', flush=True)

            time.sleep(1)

        all_results[strategy_key] = strategy_results

        # Save per-strategy results
        with open(os.path.join(outputs_dir, f'eval_thinking_{strategy_key}.json'), 'w', encoding='utf-8') as f:
            json.dump(strategy_results, f, ensure_ascii=False, indent=2)
        print(f'\nSaved: eval_results/eval_thinking_{strategy_key}.json', flush=True)
        time.sleep(2)

    # Summary
    print(f'\n{"="*60}', flush=True)
    print('FINAL COMPARISON', flush=True)
    print(f'{"="*60}', flush=True)

    summary = {}
    for strategy_key in all_results:
        scores = []
        for qa_id, result in all_results[strategy_key].items():
            if result.get('score'):
                scores.append(result['score']['weighted_score'])
        if scores:
            avg = sum(scores) / len(scores)
            summary[strategy_key] = {
                'avg_score': avg,
                'num_questions': len(scores),
                'per_question': {k: v['score'] for k, v in all_results[strategy_key].items() if v.get('score')}
            }
            print(f'\n{strategy_key} ({STRATEGIES[strategy_key]["desc"]}): {avg:.2%} avg', flush=True)
        else:
            print(f'\n{strategy_key}: NO RESULTS', flush=True)

    # Save summary
    with open(os.path.join(outputs_dir, 'eval_thinking_summary.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'questions': [{'id': q['id'], 'tags': q['tags']} for q in COMPLEX_QUESTIONS],
            'summary': summary,
            'all_results': all_results,
        }, f, ensure_ascii=False, indent=2)

    # Print ranking
    print(f'\n{"="*60}', flush=True)
    print('RANKING', flush=True)
    print(f'{"="*60}', flush=True)
    ranked = sorted(summary.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    for rank, (key, data) in enumerate(ranked, 1):
        print(f'  #{rank} {key}: {data["avg_score"]:.2%} ({STRATEGIES[key]["desc"]})')

    print(f'\nSaved: eval_results/eval_thinking_summary.json', flush=True)
    return summary


if __name__ == '__main__':
    summary = run_eval()
    print(f'\nRanking:')
    ranked = sorted(summary.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    for rank, (key, data) in enumerate(ranked, 1):
        print(f'  #{rank} {key}: {data["avg_score"]:.2%} ({STRATEGIES[key]["desc"]})')
