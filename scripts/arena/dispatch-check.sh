#!/bin/bash
# 派发前检查：scripts/arena/dispatch-check.sh <repo>
# 用法: dispatch-check.sh prompt-first-bench
# 输出: 该仓活跃会话 + 一仓一会话违规检测 + 门禁清单
set -euo pipefail
REPO="${1:?用法: dispatch-check.sh <repo>}"
DIR="$(cd "$(dirname "$0")/../../sop/arena" && pwd)"
J="$DIR/sessions.json"
[ -f "$J" ] || { echo "FATAL: $J 不存在"; exit 1; }

python3 - "$REPO" "$J" <<'EOF'
import json, sys
repo, j = sys.argv[1], sys.argv[2]
d = json.load(open(j))
ss = [s for s in d['sessions'] if s['repo'] == repo]
act = [s for s in ss if s['status'].startswith('active')]
print(f"repo: {repo}")
if not ss:
    print("  无会话记录 → 允许新开（开完立即登记 active-sessions.md + sessions.json）")
elif len(act) > 1:
    print(f"  ⚠️ 违规: {len(act)} 个 active 会话（一仓一会话硬约束）:")
    for s in act: print(f"    - {s['uuid']} ({s['taskSpace']}) {s['task']} [{s['last_date']}]")
    print("  处置: 核验哪个已完成 → 归档到 session-history.md，只留一个")
else:
    for s in act:
        print(f"  复用: {s['uuid']} (taskSpace: {s['taskSpace']})")
        print(f"        任务: {s['task']} [{s['last_date']}] 分支: {s['branch']}")
    idle = [s for s in ss if s['status'] in ('idle','done')]
    if idle:
        print(f"  (另有 {len(idle)} 个 idle/done 会话，见 sessions.json)")
print()
print("门禁清单（逐条过）:")
print("  [ ] 任务书已 commit+push 到目标仓分支（git log -1 验证 sha）")
print("  [ ] prompt 显式声明目标仓库名 + 任务书路径 + 验收标准")
print("  [ ] 回执指纹: 任务书 sha256 写入 prompt（防 agent 读旧版）")
print("  [ ] 新开会话: composer 先选 repo chip + branch chip 再发消息")
for k in d.get('known_issues', []):
    if repo in k: print(f"  ⚠️ 已知问题: {k}")
EOF
