#!/usr/bin/env python3
"""
audit-behavior.py — qqbot/agent 行为审计（量化基线）

用途：对指定 Hermes 会话做行为模式量化，验证规则修改是否生效（回归审计）。
用法：
  python3 scripts/audit-behavior.py                      # 审计最近 3 个 qqbot 会话
  python3 scripts/audit-behavior.py <session_id> ...      # 审计指定会话
  python3 scripts/audit-behavior.py --source weixin       # 换频道
  python3 scripts/audit-behavior.py --json out.json       # 机器可读输出

度量（全部机械可复算，无 LLM）：
  - delegate 次数 / 最长无 delegate 工具连击（Lead 上下文预算是否执行）
  - A/B 选项句式命中（自主决策规则：不列选项让用户挑）
  - 播报句式命中（执行纪律①：不播报进度）
  - D 纠正/打断锚点数（对齐质量：越少越好，但要看纠的是什么）

注意：A/B 和播报的正则有误报（引用 D 原话/文件名会命中），
数字是"疑似违规密度"，不是精确违规数。趋势对比 > 绝对值。
"""
import sqlite3, re, sys, os, json, argparse, datetime

DB = os.path.expanduser('~/.hermes/state.db')
# 真正的打断/纠正信号（开头或短句），避免松散词误报
PAT_CORR = re.compile(
    r'^(等等|不对|停|我发现|纠正|重来|方向错|你理解错|不是让你|我说的|机械感|零容忍|挤牙膏)'
    r'|我说的很有问题|很有问题|跑偏了|偏离了|你搞错|你弄错|错了[，。！]'
)
# A/B 选项句式（自主决策违规：列选项让 D 挑）
PAT_AB = re.compile(
    r'(你选哪|A/B|B/A|选项[ABC]|[ABC]\s*[/:：].*\n\s*[ABC]\s*[/:：]'
    r'|要不要|是否继续|你定|你拍板|你确认下|需要你定|需要你确认)'
)
# 播报句式（执行纪律①违规：播报进度）
PAT_ANN = re.compile(
    r'(在推进|已完成|等它回来|等它完成|等它跑完|派了?\s*(sub|subagent)'
    r'|正在跑|后台在跑|跑完后|回来我|回来再|预计.*前落地|已完成\s*\d+)'
)


def audit_session(db, sid):
    rows = db.execute(
        "SELECT id, role, content, tool_name, timestamp FROM messages "
        "WHERE session_id=? ORDER BY id", (sid,)
    ).fetchall()
    d_msgs = [r for r in rows if r[1] == 'user' and len(r[2] or '') < 2000]
    a_replies = [r for r in rows if r[1] == 'assistant' and len(r[2] or '') > 0]
    tools = [r for r in rows if r[1] == 'tool']
    delegates = [r for r in tools if (r[3] or '').startswith('delegate')]

    # 最长无 delegate 工具连击
    streak = mx = 0
    for r in rows:
        if r[1] == 'tool':
            if (r[3] or '').startswith('delegate'):
                streak = 0
            else:
                streak += 1
                mx = max(mx, streak)
        elif r[1] in ('user', 'assistant'):
            streak = 0

    ab_hits = sum(len(PAT_AB.findall(r[2] or '')) for r in a_replies)
    ann_hits = sum(len(PAT_ANN.findall(r[2] or '')) for r in a_replies)

    # D 纠正锚点（去重）
    anchors = []
    seen = set()
    for i, r in enumerate(rows):
        c = re.sub(r'\s+', ' ', r[2] or '')
        if r[1] == 'user' and len(c) < 1000 and PAT_CORR.search(c):
            key = c[:40]
            if key in seen:
                continue
            seen.add(key)
            nxt = ''
            for r2 in rows[i + 1:i + 40]:
                if r2[1] == 'assistant' and len(r2[2] or '') > 0:
                    nxt = re.sub(r'\s+', ' ', r2[2])[:250]
                    break
            anchors.append({'id': r[0], 'd': c[:120], 'a': nxt})

    # 会话时间窗
    ts = [r[4] for r in rows if r[4]]
    t0 = datetime.datetime.fromtimestamp(min(ts)).strftime('%m-%d %H:%M') if ts else '?'
    t1 = datetime.datetime.fromtimestamp(max(ts)).strftime('%m-%d %H:%M') if ts else '?'

    return {
        'session_id': sid,
        'window': f'{t0} → {t1}',
        'd_msgs': len(d_msgs),
        'a_replies': len(a_replies),
        'tool_calls': len(tools),
        'delegates': len(delegates),
        'max_no_delegate_streak': mx,
        'ab_pattern_hits': ab_hits,
        'announce_pattern_hits': ann_hits,
        'd_correction_anchors': len(anchors),
        'anchors': anchors,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sessions', nargs='*', help='session_id(s)')
    ap.add_argument('--source', default='qqbot', help='channel filter (qqbot/weixin/cron)')
    ap.add_argument('--limit', type=int, default=3, help='recent sessions to audit')
    ap.add_argument('--json', help='write JSON output')
    args = ap.parse_args()

    db = sqlite3.connect(DB)
    if args.sessions:
        sids = args.sessions
    else:
        cur = db.execute(
            "SELECT id FROM sessions WHERE source=? ORDER BY started_at DESC LIMIT ?",
            (args.source, args.limit)
        )
        sids = [r[0] for r in cur.fetchall()]

    results = [audit_session(db, s) for s in sids]

    # 打印对比表
    print(f"{'会话':<28} {'窗口':<20} {'D发言':>5} {'delegate':>8} {'最长无del':>8} {'A/B':>5} {'播报':>5} {'纠正':>5}")
    print('-' * 100)
    for r in results:
        print(f"{r['session_id'][:26]:<28} {r['window']:<20} {r['d_msgs']:>5} "
              f"{r['delegates']:>8} {r['max_no_delegate_streak']:>8} "
              f"{r['ab_pattern_hits']:>5} {r['announce_pattern_hits']:>5} {r['d_correction_anchors']:>5}")

    if args.json:
        with open(args.json, 'w') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nJSON → {args.json}")


if __name__ == '__main__':
    main()
