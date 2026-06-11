#!/usr/bin/env python3
"""
New eval: 测试不同 prompt 策略是否能让模型产生"预设分析→追问边界→回答"的结构。

测试变量：
- A: 无 prompt (baseline)
- B: 轻量 prompt（告诉模型"先分析问题的边界和前提条件再回答"）
- C: 完整成璟 persona + 回答结构要求
- D: 回答结构要求但不指定 persona（只说方法论）
"""

import json, urllib.request, time, os, sys

API = 'http://127.0.0.1:8000/v1/chat/completions'
MODEL = 'Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit'

# 统一测试问题
QUESTION = '什么是自由意志？'

STRATEGIES = {
    'A': {  # 无
        'system': None,
        'desc': 'baseline'
    },
    'B': {  # 预设分析
        'system': '回答问题前，先分析：1) 这个问题的本质定义是什么 2) 有哪些关键变量被忽略了 3) 问题的边界在哪里 4) 哪些地方是知识盲区。然后再给出答案。用中文回答。',
        'desc': '先分析后回答'
    },
    'C': {  # 完整 persona
        'system': '你是成璟的思考扩展。中文优先，简洁直接。回答问题前，先反复追问问题本身——判断这是什么类型的问题，所有变量是什么，哪些是知识盲区（比如实验能标不够、某个定理没有证明）。拆解任务逐步推进，不要一次给完整答案。用 ❏ 标记思考块。',
        'desc': '成璟 persona + 预设分析'
    },
    'D': {  # 方法论
        'system': '回答复杂问题时，先拆解问题：识别隐含假设、关键变量、边界条件。如果一个问题的定义本身就不完备，先修补定义再回答。用中文。',
        'desc': '方法论 only'
    }
}

def call_api(system_content, message, max_tokens=800):
    msgs = []
    if system_content:
        msgs.append({'role': 'system', 'content': system_content})
    msgs.append({'role': 'user', 'content': message})
    data = json.dumps({
        'model': MODEL, 'messages': msgs,
        'temperature': 0.8, 'max_tokens': max_tokens, 'stream': False
    }).encode()
    r = urllib.request.urlopen(urllib.request.Request(API, data=data, headers={'Content-Type': 'application/json'}), timeout=300)
    return json.loads(r.read())['choices'][0]['message']['content']

results = {}
outputs_dir = '/Users/a1-6/Desktop/workspace/projects/D1-persona-align/eval_results'
os.makedirs(outputs_dir, exist_ok=True)

for key, strat in STRATEGIES.items():
    print(f'\n=== Strategy {key}: {strat["desc"]} ===', flush=True)
    text = call_api(strat['system'], QUESTION)
    
    # Strip thinking tags
    if '</think>' in text:
        text = text.split('</think>', 1)[1].strip()
    
    results[key] = text
    print(f'Length: {len(text)} chars', flush=True)
    print(f'First 200 chars: {text[:200]}', flush=True)
    time.sleep(1)

# Save
with open(os.path.join(outputs_dir, 'eval_strategies.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'question': QUESTION,
        'strategies': {k: v['desc'] for k, v in STRATEGIES.items()},
        'results': results
    }, f, ensure_ascii=False, indent=2)

print(f'\nSaved to eval_results/eval_strategies.json', flush=True)

# Print comparison of the "meta analysis" quality
print(f'\n{"="*60}', flush=True)
print('META-ANALYSIS COMPARISON (first 150 chars after thinking)', flush=True)
print(f'{"="*60}', flush=True)
for key in sorted(results):
    text = results[key]
    snippet = text[:150]
    print(f'\n[{key}] {snippet}')
