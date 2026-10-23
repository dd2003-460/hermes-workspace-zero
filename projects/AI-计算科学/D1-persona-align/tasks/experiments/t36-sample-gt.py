#!/usr/bin/env python3
"""T36: 从 corpus 分层采样 10 条 GT（5 场景 × 单条/多轮）

场景定义（基于 corpus 内容分类）：
- S1: 技术讨论（物理/数学/AI 技术）
- S2: 量化估算（排名/概率/精度）
- S3: 元评估（AI 能力/自我审视）
- S4: 个人暴露（心理状态/自我质疑）
- S5: 混合（技术+个人+估算）

采样策略：
- 每个场景采样 2 条（1 单条 + 1 多轮）
- 单条 = 一条 MSG（<200 字）
- 多轮 = 连续 3-5 条 MSG（总 500-1000 字）
- 优先选有括号插话/编号跳跃/中断特征的样本

输出：tasks/experiments/t36-gt-samples.json
"""
import json
import re
from pathlib import Path

CORPUS = Path("/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-persona-align/research/corpus/ai-chat/corpus_input.txt")
OUTPUT = Path("/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-persona-align/tasks/experiments/t36-gt-samples.json")

def parse_corpus(text: str) -> list[dict]:
    """解析 corpus 为 MSG 列表"""
    messages = []
    current_id = None
    current_lines = []
    for line in text.split('\n'):
        m = re.match(r'^--- MSG (\d+) ---$', line.strip())
        if m:
            if current_id is not None:
                messages.append({
                    'id': current_id,
                    'content': '\n'.join(current_lines).strip()
                })
            current_id = int(m.group(1))
            current_lines = []
        elif current_id is not None:
            current_lines.append(line)
    if current_id is not None:
        messages.append({
            'id': current_id,
            'content': '\n'.join(current_lines).strip()
        })
    return messages

def classify_scene(content: str) -> str:
    """基于关键词分类场景（更宽松）"""
    tech_keywords = ['模型', '算法', '训练', '推理', 'API', 'prompt', 'token', 'GPU', 'vLLM',
                     '物理', '数学', '量子', '神经网络', 'transformer', 'attention', '解码', '生成', '带宽', '计算']
    quant_keywords = ['估算', '排名', '概率', '精度', '置信度', '量化', '统计', '排名', '水平', '评价']
    meta_keywords = ['自我审视', '自省', 'taste', '自我觉察', '反思', '质疑', '不确定', '看法', '意见']
    personal_keywords = ['我觉得', '我猜', '我傲慢', '我烦', '我担心', '我害怕', '我想知道', '我', '你']

    content_lower = content.lower()
    scores = {
        'S1': sum(1 for kw in tech_keywords if kw in content_lower),
        'S2': sum(1 for kw in quant_keywords if kw in content_lower),
        'S3': sum(1 for kw in meta_keywords if kw in content_lower),
        'S4': sum(1 for kw in personal_keywords if kw in content_lower),
    }

    # 检查中断特征（括号插话/编号跳跃）
    has_paren = '（' in content or '(' in content
    has_numbering = bool(re.search(r'\d+\.\d+', content))

    # S5 = 混合场景（有中断特征且内容较长）
    if (has_paren or has_numbering) and len(content) > 500:
        return 'S5'

    max_score = max(scores.values())
    if max_score == 0:
        return 'S1'  # 默认
    return [k for k, v in scores.items() if v == max_score][0]

def has_interrupt_features(content: str) -> bool:
    """检查是否有中断特征（括号插话/编号跳跃/截断）"""
    features = []
    # 括号插话
    if '（' in content or '(' in content:
        features.append('paren')
    # 编号跳跃
    numbers = re.findall(r'(\d+)\.(\d+)', content)
    if numbers:
        nums = [int(n[1]) for n in numbers]
        if len(nums) > 1 and any(nums[i+1] - nums[i] > 1 for i in range(len(nums)-1)):
            features.append('number_jump')
    # 截断（句子未结束）
    if content.endswith(('，', '、', '。', '！', '？')) is False and len(content) > 50:
        features.append('truncation')
    return features

def sample_gt(messages: list[dict]) -> dict:
    """分层采样 10 条 GT"""
    # 按场景分类
    scenes = {f'S{i}': [] for i in range(1, 6)}
    for msg in messages:
        if not msg['content']:
            continue
        scene = classify_scene(msg['content'])
        scenes[scene].append(msg)

    # 每个场景采样 2 条（1 单条 + 1 多轮）
    samples = {}
    for scene in ['S1', 'S2', 'S3', 'S4', 'S5']:
        candidates = scenes[scene]
        if not candidates:
            samples[scene] = {'single': None, 'multi': None}
            continue

        # 单条：选短消息（<200 字）
        single_candidates = [m for m in candidates if len(m['content']) < 200]
        single = single_candidates[0] if single_candidates else candidates[0]

        # 多轮：选连续 3-5 条消息
        multi = None
        for i in range(len(candidates) - 2):
            group = candidates[i:i+4]  # 最多 4 条
            total_len = sum(len(m['content']) for m in group)
            if 300 < total_len < 1200:
                multi = group
                break
        if multi is None:
            multi = candidates[:3]  # 默认前 3 条

        samples[scene] = {
            'single': {
                'id': single['id'],
                'content': single['content'],
                'features': has_interrupt_features(single['content']),
                'char_count': len(single['content'])
            },
            'multi': {
                'ids': [m['id'] for m in multi],
                'content': '\n---\n'.join(m['content'] for m in multi),
                'features': has_interrupt_features('\n'.join(m['content'] for m in multi)),
                'char_count': sum(len(m['content']) for m in multi),
                'msg_count': len(multi)
            }
        }

    return samples

def main():
    text = CORPUS.read_text()
    messages = parse_corpus(text)
    print(f"Parsed {len(messages)} messages from corpus")

    samples = sample_gt(messages)

    # 统计
    total_chars = 0
    for scene, data in samples.items():
        if data['single']:
            total_chars += data['single']['char_count']
        if data['multi']:
            total_chars += data['multi']['char_count']
        print(f"{scene}: single={data['single']['char_count'] if data['single'] else 0} chars, "
              f"multi={data['multi']['char_count'] if data['multi'] else 0} chars")

    print(f"\nTotal: {total_chars} chars")

    # 保存
    OUTPUT.write_text(json.dumps(samples, ensure_ascii=False, indent=2))
    print(f"\nSaved to {OUTPUT}")

if __name__ == '__main__':
    main()
