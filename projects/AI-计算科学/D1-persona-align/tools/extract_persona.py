#!/usr/bin/env python3
"""从 Claude Code 对话日志中提取 persona 证据，更新 unified_profile。

用法: python3 extract_persona.py [--source PATH] [--diff-only]

默认扫描 ~/.claude/projects/-Users-a1-6/ 下的所有 jsonl 对话日志，
提取用户对 AI 的偏好指示、思维模式、决策方式等证据，
生成 unified_profile 的更新建议。
"""
import json
import os
import sys
import re
import argparse
from collections import Counter, defaultdict
from datetime import datetime

CONV_DIR = os.path.expanduser("~/.claude/projects/-Users-a1-6/")

# 要提取的证据类型
EVIDENCE_TYPES = {
    'expression_style': {
        'keywords': ['简洁', '直接', '不要', '避免', '少', '不要重复', '不要废话',
                      '中文优先', '英文', '不要用英文', 'markdown', '表格', '列表'],
        'description': '表达风格 — 对输出格式、语言、结构的要求',
    },
    'thinking_pattern': {
        'keywords': ['因果', '变量', '混淆', '边界', '条件', '假设', '分析',
                      '贝叶斯', '溯因', '概率', '推断', '决策', '权衡'],
        'description': '思维模式 — 用户展示的分析方法和推理方式',
    },
    'decision_method': {
        'keywords': ['优先级', '应该', '必须', '不要做', '做这个', '选', '决策',
                      '置信度', '风险', '自主', '等待', '先', '然后'],
        'description': '决策方法 — 用户如何做出选择和排序',
    },
    'value_function': {
        'keywords': ['重要', '核心', '底线', '原则', '红线', '永远', '不要',
                      '对齐', '诚实', '安全', '质量', '效率'],
        'description': '价值函数 — 用户的核心价值观和优先级',
    },
    'behavior_trait': {
        'keywords': ['重复', '机械', '废话', '确认', '验证', '自己看', '自己查',
                      '主动', '自主', '不等', '跳过'],
        'description': '行为特质 — 用户不喜欢和喜欢的交互方式',
    },
}

# 过滤掉常见的无关词汇
IGNORE_PATTERNS = [
    r'^//',  # 代码注释
    r'^\s*#',  # Python 注释
    r'{"role":\s*"assistant"',  # AI 说的话（只分析用户输入）
]


def parse_jsonl_line(line):
    """解析 jsonl 行，提取 user 消息"""
    line = line.strip()
    if not line:
        return None
    try:
        data = json.loads(line)
        if isinstance(data, dict) and 'message' in data:
            msg = data['message']
            if isinstance(msg, dict):
                role = msg.get('role', '')
                if role == 'user':
                    content = msg.get('content', '')
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, list):
                        # Array of content blocks
                        texts = []
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                texts.append(block.get('text', ''))
                        return ' '.join(texts)
        elif isinstance(data, dict) and 'text' in data:
            # Alternative format
            role = data.get('role', '')
            if role == 'user':
                return data['text']
        return None
    except json.JSONDecodeError:
        return None


def extract_evidence(texts, evidence_types):
    """从用户文本中提取证据"""
    combined = '\n'.join(texts)
    combined = combined.lower()

    results = {}
    for etype, config in evidence_types.items():
        matches = []
        for kw in config['keywords']:
            for match in re.finditer(re.escape(kw), combined):
                start = max(0, match.start() - 100)
                end = min(len(combined), match.end() + 100)
                context = combined[start:end].strip()
                matches.append({
                    'keyword': kw,
                    'context': context,
                    'position': match.start(),
                })
        if matches:
            results[etype] = {
                'description': config['description'],
                'matches': matches[:10],  # 最多保留10条
                'count': len(matches),
            }
    return results


def extract_personas_from_messages(texts):
    """从用户消息中提取显式的 persona 指示"""
    results = {
        'direct_instructions': [],
        'corrections': [],
        'preferences': [],
    }

    for text in texts:
        lower = text.lower()

        # 直接指示 — "不要...", "不要...", "不要...", "不要..."
        for pattern in [
            r'不要[^.。]*[\.。]',
            r'避免[^.。]*[\.。]',
            r'别[^.。]*[\.。]',
            r'少[^.。]*[\.。]',
            r'禁止[^.。]*[\.。]',
        ]:
            for match in re.finditer(pattern, text):
                results['direct_instructions'].append(match.group(0))

        # 纠正 — 用户纠正 AI 的行为
        for pattern in [
            r'(不是|不对|错误|错|混淆|搞错)',
            r'(你再|你又)',
        ]:
            if re.search(pattern, text):
                results['corrections'].append(text[:200])

        # 偏好表达 — "我喜欢", "我希望", "我要", "我偏好", "应该是"
        for pattern in [
            r'我喜欢.*[\.。]',
            r'我希望.*[\.。]',
            r'我要.*[\.。]',
            r'我偏好.*[\.。]',
            r'应该(是|该).*[\.。]',
            r'(最好|更好的).*[\.。]',
        ]:
            for match in re.finditer(pattern, text):
                results['preferences'].append(match.group(0))

    return results


def scan_conversations(conversations):
    """扫描所有对话，提取 persona 证据"""
    all_evidence = defaultdict(list)
    all_personas = {k: [] for k in extract_personas_from_messages([]).keys()}
    sessions_with_evidence = 0

    for session_id, msgs in conversations.items():
        if not msgs:
            continue

        # 提取显式 persona 指示
        personas = extract_personas_from_messages(msgs)
        for key in all_personas:
            all_personas[key].extend(personas[key])

        # 提取关键词证据
        evidence = extract_evidence(msgs, EVIDENCE_TYPES)
        has_evidence = any(v['count'] > 0 for v in evidence.values())

        if has_evidence:
            sessions_with_evidence += 1
            for etype, data in evidence.items():
                for match in data['matches']:
                    all_evidence[etype].append({
                        'session': session_id,
                        'keyword': match['keyword'],
                        'context': match['context'],
                    })

    return {
        'evidence': dict(all_evidence),
        'personas': all_personas,
        'sessions_scanned': len(conversations),
        'sessions_with_evidence': sessions_with_evidence,
    }


def load_conversations(conversations_dir):
    """从 jsonl 文件加载对话"""
    conversations = {}
    processed = 0

    for filename in os.listdir(conversations_dir):
        if not filename.endswith('.jsonl'):
            continue

        filepath = os.path.join(conversations_dir, filename)
        session_id = filename.replace('.jsonl', '')
        msgs = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    result = parse_jsonl_line(line)
                    if result:
                        msgs.append(result)
                        processed += 1
                        # 只取前500条用户消息 per session (效率考虑)
                        if len(msgs) >= 500:
                            break
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        if msgs:
            conversations[session_id] = msgs

    return conversations


def main():
    parser = argparse.ArgumentParser(description='从对话日志中提取 persona 证据')
    parser.add_argument('--source', default=CONV_DIR, help='对话日志目录')
    parser.add_argument('--limit', type=int, default=500, help='每 session 最大消息数')
    args = parser.parse_args()

    print(f"扫描对话目录: {args.source}")

    conversations = load_conversations(args.source)
    print(f"加载了 {len(conversations)} 个会话，{sum(len(m) for m in conversations.values())} 条用户消息")

    results = scan_conversations(conversations)
    print(f"\n扫描完成:")
    print(f"  会话总数: {results['sessions_scanned']}")
    print(f"  有证据的会话: {results['sessions_with_evidence']}")

    print(f"\n=== 显式指示 (不要/避免/少/别) ===")
    instruction_counts = Counter(results['personas']['direct_instructions'])
    for instr, count in instruction_counts.most_common(20):
        print(f"  [{count}x] {instr[:100]}")

    print(f"\n=== 偏好表达 (希望/喜欢/要/偏好/应该) ===")
    pref_counts = Counter(results['personas']['preferences'])
    for pref, count in pref_counts.most_common(20):
        print(f"  [{count}x] {pref[:100]}")

    print(f"\n=== 纠正 (用户纠正 AI) ===")
    for corr in results['personas']['corrections'][:20]:
        print(f"  {corr[:150]}")

    print(f"\n=== 关键词证据 ===")
    for etype, data in results['evidence'].items():
        print(f"\n  {etype}: {len(data)} 条证据")
        keyword_counts = Counter(d['keyword'] for d in data)
        for kw, count in keyword_counts.most_common(5):
            print(f"    [{kw}] {count}次")

    # 输出 JSON 供后续处理
    print(f"\n=== JSON 输出 ===")
    summary = {
        'sessions_scanned': results['sessions_scanned'],
        'sessions_with_evidence': results['sessions_with_evidence'],
        'top_instructions': dict(instruction_counts.most_common(10)),
        'top_preferences': dict(pref_counts.most_common(10)),
        'evidence_summary': {k: len(v) for k, v in results['evidence'].items()},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
