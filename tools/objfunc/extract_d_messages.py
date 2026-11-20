#!/usr/bin/env python3
"""提取 D 的历史直聊消息 → JSON（objfunc-signal-log 素材源）

来源判定（三层过滤）：
1. 会话来源：weixin/qqbot/cli/tui = D 直聊；cron/subagent/api_server/oneshot 排除
   （cron 会话里没有 D 的话，全是调度指令/hook）
2. 消息特征：直聊会话里仍混有 hook 注入，按前缀剔除：
   - [来源: ... · 非用户消息]   → hook 续推提醒
   - [规则注入 / [阶段状态机    → 规则/状态机注入
   - [OUT-OF-BAND USER MESSAGE → 压缩重放标记（内容本身是 D 的话，保留正文）
   - 全自动停止门 / 停止提醒    → stop_hook
   - 引用: / Quoted message    → 引用转发（内容可能是 D 也可能是我，标记存疑）
   - COMPACTION 摘要           → 压缩产物
3. 去重：
   - hook 类：按"前缀模式"去重（同一 hook 重复 N 次只留 1 条 + 计数）
   - 真消息：按 (来源, 内容) 精确去重（D 复制粘贴同一句的情况）

输出：JSON，每条 {ts, source, session_id, msg_id, kind, content}
kind: real | quoted | hook_deduped(计数)
"""
import sqlite3, json, re, sys
from collections import Counter
from datetime import datetime, timezone, timedelta

DB = '/Users/a1-6/.hermes/state.db'
OUT = '/Users/a1-6/Desktop/workspace/tools/objfunc/d-messages.json'
CST = timezone(timedelta(hours=8))

# 会话来源 → 是否 D 直聊
DIRECT = {'weixin', 'qqbot', 'cli', 'tui'}

# hook 前缀（按顺序匹配，先长后短）
HOOK_PATTERNS = [
    ('hook_stop', re.compile(r'^\[来源: stop_hook')),
    ('hook_nonuser', re.compile(r'^\[来源: [^\]]*· 非用户消息')),
    ('hook_rules', re.compile(r'^\[规则注入')),
    ('hook_stagemachine', re.compile(r'^\[阶段状态机')),
    ('hook_stogate', re.compile(r'^\[全自动停止门')),
    ('hook_storeminder', re.compile(r'^\[停止提醒')),
    ('hook_compaction', re.compile(r'CONTEXT COMPACTION|Historical Task Snapshot')),
    ('hook_tasklist', re.compile(r'^\[?Your active task list was preserved')),
    ('hook_quoted_msg', re.compile(r'^Quoted message')),
    ('hook_async', re.compile(r'^\[?(ASYNC DELEGATION BATCH COMPLETE|The user sent an image~|RALPH LOOP R\d|STATUS|Continuing toward your standing goal)')),
    ('hook_bgproc', re.compile(r'^\[?(IMPORTANT:|SYSTEM:|BACKGROUND) Background process')),
    ('hook_system', re.compile(r'^(SYSTEM:|System:)')),
    ('hook_workspace', re.compile(r'^Workspace: ')),
]
QUOTED_PATTERNS = [
    ('quoted', re.compile(r'^(引用:|Quoted message)')),
]

# 前缀元数据（剥掉后保留正文；D 的话跟在后面）
PREFIX_STRIP = [
    re.compile(r'^\[Workspace: [^\]]*\]\s*'),
    re.compile(r'^\[System note: [^\]]*\]\s*'),
    re.compile(r'^\[SYSTEM: You are running as a scheduled cron job[^\]]*\]\s*'),
    re.compile(r'^\[System: [^\]]*\]\s*'),
]

def classify(content: str):
    """返回 (kind, hook_name)。kind: real/quoted/hook"""
    for name, pat in HOOK_PATTERNS:
        if pat.search(content):
            return 'hook', name
    for name, pat in QUOTED_PATTERNS:
        if pat.search(content):
            return 'quoted', name
    return 'real', None

def strip_prefixes(content: str) -> str:
    changed = True
    while changed:
        changed = False
        for pat in PREFIX_STRIP:
            new = pat.sub('', content, count=1)
            if new != content:
                content, changed = new, True
    return content

# 纯系统元数据（剥完前缀后没正文的整条剔除）
PURE_META = [
    re.compile(r'^\[System note:'),
    re.compile(r'^\[SYSTEM: You are running as a scheduled cron job'),
    re.compile(r'^\[System: Your previous response was truncated'),
]

def is_pure_meta(content: str) -> bool:
    for pat in PURE_META:
        if pat.search(content):
            return True
    return False

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    rows = cur.execute("""
        SELECT m.id, m.session_id, s.source, m.timestamp, m.content
        FROM messages m JOIN sessions s ON m.session_id = s.id
        WHERE m.role='user' AND m.active=1 AND s.source IN ('weixin','qqbot','cli','tui')
        ORDER BY m.timestamp
    """).fetchall()

    out = []
    hook_counts = Counter()
    hook_samples = {}
    seen_real = set()

    for msg_id, session_id, source, ts, content in rows:
        if not content:
            continue
        content = content.strip()
        # OUT-OF-BAND 重放：剥掉标记保留正文
        m = re.match(r'^\[OUT-OF-BAND USER MESSAGE[^\]]*\]\s*(.*?)\s*\[/OUT-OF-BAND USER MESSAGE\]$',
                     content, re.S)
        if m:
            content = m.group(1).strip()
        kind, name = classify(content)
        if kind == 'hook':
            hook_counts[name] += 1
            hook_samples.setdefault(name, content[:200])
            continue
        if kind == 'quoted':
            out.append({'ts': ts, 'source': source, 'session_id': session_id,
                        'msg_id': msg_id, 'kind': 'quoted', 'content': content})
            continue
        # real：剥前缀元数据（[System note:...] 等），剥完再判
        content = strip_prefixes(content).strip()
        if not content:
            hook_counts['meta_only'] += 1
            continue
        if content.startswith('[') and (content.startswith('[引用:') or content.startswith('[System')):
            # 剥完还是系统/引用内容（如 System note 后跟 cron 引用）→ 存疑
            out.append({'ts': ts, 'source': source, 'session_id': session_id,
                        'msg_id': msg_id, 'kind': 'quoted', 'content': content})
            continue
        # real：精确去重
        key = (source, content)
        if key in seen_real:
            continue
        seen_real.add(key)
        out.append({'ts': ts, 'source': source, 'session_id': session_id,
                    'msg_id': msg_id, 'kind': 'real', 'content': content})

    result = {
        'extracted_at': datetime.now(CST).isoformat(),
        'db': DB,
        'sessions_scanned': sorted(DIRECT),
        'totals': {
            'raw_user_msgs_in_direct_sessions': len(rows),
            'real_unique': sum(1 for x in out if x['kind'] == 'real'),
            'quoted': sum(1 for x in out if x['kind'] == 'quoted'),
            'hook_deduped': dict(hook_counts),
        },
        'hook_samples': hook_samples,
        'messages': out,
    }
    with open(OUT, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"raw={len(rows)} real={result['totals']['real_unique']} "
          f"quoted={result['totals']['quoted']} hooks={sum(hook_counts.values())}")
    print("hook 分布:", dict(hook_counts))
    print(f"→ {OUT}")

if __name__ == '__main__':
    main()
