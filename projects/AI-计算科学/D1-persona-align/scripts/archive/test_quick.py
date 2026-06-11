#!/usr/bin/env python3
"""快速测试：persona_profile_v2 vs method_only vs chenglu_persona（v2 验证）"""
import json, urllib.request, time

API = 'http://127.0.0.1:8000/v1/chat/completions'
MODEL = 'Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit'

# V2 精简版 — ~100 字符，收敛设计
PERSONA_PROFILE_V2 = '''分析：1)识别变量 2)区分因果 3)考虑混淆 4)明确边界 5)标不确定度
表达：中文优先，简洁直接，少空话多证据
自省：每结论问——Impact? Bias? Motivation?
决策：对齐>效率，边界内自主，对标世界顶尖'''

# method_only — 80 字符
METHOD_ONLY = '你是一个研究者。分析问题时必须：1) 识别关键变量 2) 区分相关和因果 3) 考虑可能的混淆因素 4) 明确你的结论在什么条件下成立。用中文。'

# chenglu_persona — 现有 persona
CHENG_LU_PERSONA = '''你是成璐的AI助手。你的思维特征：
1. 贝叶斯思维：先验→证据→后验→新先验，闭环
2. 信息论视角：语言/数学/物理/社会都是同一信息处理机制的不同信道
3. 直觉是高维推理的压缩，追问"你说的意思是…？"
4. 概率是动力学下的信息抹除
5. 简洁直接，先证据后结论
6. 遇到复杂问题先拆解，考虑多路径，不急于下结论

用中文回答。'''

QUESTIONS = [
    {
        'id': 'agent_capability_test',
        'question': '如果让一个 AI agent 独立完成一个大型工程项目（如 coding 任务），它需要具备哪些核心能力？如何评估它的规划能力是否充分？',
    },
    {
        'id': 'causal_inference_test',
        'question': '研究表明，每天使用社交媒体超过3小时的人抑郁率更高。能否得出"使用社交媒体导致抑郁"的结论？如果一项城市交通实验在某个城市证明了公交专用道能显著降低通勤时间，这项结果对其他城市的有效边界是什么？',
    },
]

STRATEGIES = {
    'persona_profile_v2': {'system': PERSONA_PROFILE_V2, 'desc': 'persona_profile_v2 (~100 chars)'},
    'method_only': {'system': METHOD_ONLY, 'desc': 'method_only (80 chars)'},
    'chenglu_persona': {'system': CHENG_LU_PERSONA, 'desc': 'chenglu_persona (200 chars)'},
}


def call_api(system_content, message, max_tokens=3000, temperature=0.8):
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
    """修正版评分 — 去掉长度偏向，注重分析密度"""
    text_len = len(response)

    depth_keywords = ['混淆', '因果', '相关', '机制', '形式化', '边界', '条件', '变量', '假设', '替代', '控制']
    uncertainty_words = ['可能', '不确定', '需要验证', '假设', '如果...则', '未必', '取决于']
    analysis_words = ['内生', '外生', '混淆', '指标', '基准', '对照', '鲁棒']

    depth_count = sum(response.count(kw) for kw in depth_keywords)
    uncertainty_count = sum(response.count(w) for w in uncertainty_words)
    analysis_count = sum(response.count(w) for w in analysis_words)

    # 修正：不再以长度为正向指标
    score = {
        'depth': min(1, depth_count / 5),          # 深度分析覆盖
        'uncertainty': min(1, uncertainty_count / 3),  # 不确定性标注
        'analysis_density': min(1, analysis_count / max(1, text_len) * 1000),  # 分析术语密度
        'structure': 1.0 if text_len > 200 and text_len < 5000 else 0.5,  # 合理长度范围内
    }

    weights = {'depth': 2.0, 'uncertainty': 1.0, 'analysis_density': 1.5, 'structure': 0.5}
    total = sum(score[k] * weights[k] for k in score)
    max_w = sum(weights[k] for k in score)

    score['weighted_score'] = total / max_w
    return score


results = {}
for strategy_key, strategy in STRATEGIES.items():
    print(f'\n=== {strategy_key}: {strategy["desc"]} ===', flush=True)
    print(f'Prompt length: {len(strategy["system"])} chars', flush=True)

    text = call_api(strategy['system'], QUESTIONS[1]['question'])
    if '</think>' in text:
        text = text.split('</think>', 1)[1].strip()

    score = score_response(text, QUESTIONS[1])
    results[strategy_key] = {'score': score, 'length': len(text), 'text': text}

    print(f'  Score: {score["weighted_score"]:.2%} | Length: {len(text)} chars', flush=True)
    print(f'  Depth: {score["depth"]:.2f}, Uncertainty: {score["uncertainty"]:.2f}, Density: {score["analysis_density"]:.2f}', flush=True)

# Print comparison
print(f'\n{"="*60}', flush=True)
print('COMPARISON', flush=True)
print(f'{"="*60}', flush=True)

for key in sorted(results, key=lambda k: results[k]['score']['weighted_score'], reverse=True):
    r = results[key]
    print(f'  {key}: {r["score"]["weighted_score"]:.2%} | {r["length"]} chars', flush=True)
