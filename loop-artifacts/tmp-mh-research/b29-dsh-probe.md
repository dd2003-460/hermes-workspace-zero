[assistant • bash]
{"command":"cd /Users/a1-6/Desktop/workspace && ls -la .hooks/ 2>/dev/null && echo \"===== rules.json =====\" && cat .hooks/rules.json 2>/dev/null && echo \"===== anchors.json =====\" && cat .hooks/anchors.json 2>/dev/null && echo \"===== engine.py 头部 =====\" && head -60 .hooks/engine.py 2>/dev/null","description":"读 .hooks 引擎与规则数据现状"}

[tool • bash]
total 88
drwxr-xr-x@  9 a1-6  staff    288 Oct 20 02:26 .
drwxr-xr-x@ 46 a1-6  staff   1472 Oct 21 21:49 ..
-rw-------@  1 a1-6  staff   4893 Oct 18 17:26 README.md
-rw-------@  1 a1-6  staff   4993 Oct 19 02:43 TEST-RESULTS.md
drwxr-xr-x@  3 a1-6  staff     96 Oct 20 00:10 __pycache__
-rw-------@  1 a1-6  staff   1127 Oct 18 14:52 anchors.json
-rw-------@  1 a1-6  staff  15260 Oct 19 01:59 engine.py
-rw-------@  1 a1-6  staff   5050 Oct 20 02:26 rules.json
drwxr-xr-x@  4 a1-6  staff    128 Oct 20 00:10 state
===== rules.json =====
{
  "version": 1,
  "config": {
    "thinking_budget_tokens": 512
  },
  "_doc": "模型可写数据。seam ∈ SessionStart|UserPromptSubmit|PreToolUse|PostToolUse|Stop。trigger 是谓词数组（OR 级联，便宜的放前）。action.inject → 模型可见提醒; action.deny → 阻塞理由（仅用于不可逆操作保护; 提醒类一律用 inject）。cooldown_turns = 最近 N 个不同 turn 内最多触发一次。改完即生效（每次事件实时读取，无需重启）。顶层 config = 全局数字配置，inject/deny 文本可用 {key} 引用（缺键原样保留）。",
  "rules": [
    {
      "id": "session-orientation",
      "seam": "SessionStart",
      "enabled": true,
      "trigger": [
        {
          "type": "always"
        }
      ],
      "action": {
        "inject": "本 workspace 装有 memory-hooks（.hooks/）：固定引擎在 5 个拦截缝实时读 rules.json 并注入提醒——L0 简单问题防过度思考、单 turn 工具调用过多防发散、不可逆命令保护、领域锚点（记忆优先）。发现新的'遗忘/过度思考'模式时，直接编辑 .hooks/rules.json 加一条规则即可（改数据不重启；格式见 .hooks/README.md）。"
      },
      "cooldown_turns": 2
    },
    {
      "id": "overthink-guard-l0",
      "seam": "UserPromptSubmit",
      "enabled": true,
      "trigger": [
        {
          "type": "keyword",
          "any": [
            "?",
            "？",
            "吗",
            "什么是",
            "是谁",
            "多少",
            "几点",
            "在哪",
            "对吗",
            "是不是"
          ],
          "max_len": 120
        }
      ],
      "action": {
        "inject": "⚡ L0 检测：这条 prompt 看起来是简单问题（短+疑问式）。先给直接结论，不展开长推理；仅当实际涉及不可逆/高风险/多步依赖时才升级思考（深度∝不可逆性，不∝长度）。若判断错了忽略本提醒。"
      },
      "cooldown_turns": 2
    },
    {
      "id": "ralph-never-stop",
      "seam": "Stop",
      "enabled": true,
      "trigger": [
        {
          "type": "always"
        }
      ],
      "action": {
        "deny": "🔄 RALPH loop：不要停止。检查当前任务是否真正完成（可验证产出）；若未完成，继续下一步；若已完成，给出结论并等待新指令。永不说'等你确认我就...'然后停滞。"
      },
      "cooldown_turns": 0
    },
    {
      "id": "overthink-backstop",
      "seam": "Stop",
      "enabled": true,
      "trigger": [
        {
          "type": "metric",
          "field": "tool_calls_this_turn",
          "op": ">=",
          "value": 8
        }
      ],
      "action": {
        "deny": "⚠️ 本 turn 已调用 8+ 次工具（过度发散信号）。收敛检查：任务真的需要这么多步吗？能否用已有结果直接给结论？若确实复杂，说明理由后继续。"
      },
      "cooldown_turns": 2
    },
    {
      "id": "irreversible-op-guard",
      "seam": "PreToolUse",
      "enabled": true,
      "trigger": [
        {
          "type": "keyword",
          "any": [
            "rm -rf",
            "rm -fr",
            "git push --force",
            "git push -f",
            "drop table",
            "truncate",
            "chmod 777",
            "> /dev/sd",
            "dd if=",
            "mkfs",
            ":(){ :|:& };:",
            "kill -9 1"
          ],
          "regex": false
        }
      ],
      "action": {
        "deny": "🛑 检测到高不可逆命令。执行前必须：①确认目标路径是预期的；②留回滚点（备份/dry-run/commit）。这是唯一使用硬阻塞的场景——若误报（实际是可逆常规操作），在下一条命令里说明并继续。"
      },
      "cooldown_turns": 1
    },
    {
      "id": "domain-anchor",
      "seam": "UserPromptSubmit",
      "enabled": true,
      "trigger": [
        {
          "type": "lexicon",
          "min_hits": 2
        }
      ],
      "action": {
        "inject": "📌 领域锚点命中（见 stderr 调试或 .hooks/state/ 的 via 记录）：先读对应 projects/ 下的 INDEX.md 与 memory/（记忆优先，避免重复探索已验证结论），再动手。"
      },
      "cooldown_turns": 2
    },
    {
      "id": "thinking-budget-frame",
      "seam": "UserPromptSubmit",
      "enabled": true,
      "trigger": [
        {
          "type": "always"
        }
      ],
      "action": {
        "inject": "🎯 本会话思考预算 {thinking_budget_tokens} tokens（深度∝不可逆性，不∝复杂度）。若思考已接近/超过预算仍未收敛：停，回看自适应思考原则（AGENTS.md「思考预算」节 / projects/AI-计算科学/D1-persona-align/thinking-budget.md）——L0/L1 可逆任务直接给结论不展开，L2 才推演一次。若当前问题本来就简单，直接答，忽略本提醒。"
      },
      "cooldown_turns": 8
    }
  ]
}===== anchors.json =====
{
  "version": 1,
  "dims": 256,
  "ngram": 3,
  "_doc": "领域锚库。每个 domain 的 keywords 用于：①离线特征哈希向量（char n-gram → dims 维，余弦相似度）；②未来可换成真实 embedder 预计算的 vector（同 domain 提供 vector 字段即覆盖）。threshold 在 rules.json 的 vector 谓词里调。",
  "domains": [
    {
      "domain": "quant",
      "label": "量化金融/资金流",
      "keywords": ["量化", "资金流", "因子", "alpha", "回测", "北向", "tick", "涨停", "跌停", "游资", "龙虎榜", "主力", "筹码", "quant", "capital flow", "backtest", "alpha factor"]
    },
    {
      "domain": "persona",
      "label": "人格/公理对齐",
      "keywords": ["公理", "压缩", "延续", "置信度", "数字分身", "思考预算", "信念", "概率", "persona", "axiom", "compression", "belief"]
    },
    {
      "domain": "gpu-inference",
      "label": "GPU推理/硬件",
      "keywords": ["gpu", "推理", "显存", "kernel", "cuda", "量化推理", "w8a16", "batch", "吞吐", "延迟", "inference", "memory bound", "tensor core"]
    }
  ]
}
===== engine.py 头部 =====
#!/usr/bin/env python3
"""DSH memory-hooks engine — 固定解释器。

模型只写数据（rules.json / anchors.json），本文件做逻辑，不改。
每次 hook 事件: 子进程被桥接拉起 → 读 stdin payload → 实时读规则 → 评估触发 → stdout 输出 JSON 决策。

输出契约（stdout, 单一 JSON 对象, 无则不输出）:
  {"additionalContext": "..."}            模型可见提醒（UserPromptSubmit/PostToolUse/SessionStart）
  {"decision":"deny","reason":"..."}      UserPromptSubmit=拒 prompt; PreToolUse=阻工具;
                                          PostToolUse=阻结果+反馈; Stop=steer 强制再走一步
  两者可同出（PostToolUse 支持; 其余事件桥接自行取用有效字段）

诊断/错误 → stderr 与 state/ 日志，绝不污染 stdout，绝不 crash（异常时静默 exit 0）。
HOOK_DEBUG=1 时把评估细节打到 stderr。
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(ROOT, "state")
RULES_PATH = os.path.join(ROOT, "rules.json")
ANCHORS_PATH = os.path.join(ROOT, "anchors.json")
LEDGER_MAX_LINES = 5000
LEDGER_KEEP = 2000

DEBUG = os.environ.get("HOOK_DEBUG") == "1"


def log_err(msg):
    if DEBUG:
        print(msg, file=sys.stderr)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def render(text, config):
    """把文本里的 {key} 替换为 config[key]（缺键则原样保留）。
    让模型改一个数字（config）即可更新所有提醒里的预算值，不逐条改文本。"""
    s = str(text or "")
    if not config or "{" not in s:
        return s
    def repl(m):
        k = m.group(1)
        return str(config[k]) if k in config else m.group(0)
    return re.sub(r"\{(\w+)\}", repl, s)


# ---------- state ledger（A4 观察律：每个组件被测量） ----------


[assistant • bash]
{"command":"cd /Users/a1-6/Desktop/workspace && sed -n '60,200p' .hooks/engine.py","description":"继续读 engine.py 谓词与 metric 实现"}

[tool • bash]
# ---------- state ledger（A4 观察律：每个组件被测量） ----------

def _safe_sid(session_id):
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(session_id or "unknown"))[:64]


def ledger_path(session_id):
    return os.path.join(STATE_DIR, _safe_sid(session_id) + ".jsonl")


def ledger_append(session_id, rec):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        p = ledger_path(session_id)
        lines = 0
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            lines = 1
        # 轮转: 超限时只留尾部
        try:
            with open(p, encoding="utf-8") as f:
                n = sum(1 for _ in f)
            if n > LEDGER_MAX_LINES:
                with open(p, encoding="utf-8") as f:
                    tail = f.readlines()[-LEDGER_KEEP:]
                with open(p, "w", encoding="utf-8") as f:
                    f.writelines(tail)
        except Exception:
            pass
    except Exception:
        pass  # 状态写入失败不影响 hook 输出


def ledger_scan(session_id, turn_id):
    """单次遍历账本 → (本 turn 工具调用数, 累计工具调用数, turn 出现序,
    每规则最后触发 turn 的下标, 每规则最后触发的 turn_id)。"""
    turn_order, turn_idx = [], {}
    t_calls, tot, last_fire, last_fire_turn = 0, 0, {}, {}
    p = ledger_path(session_id)
    if not os.path.exists(p):
        return t_calls, tot, turn_order, last_fire, last_fire_turn
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                tid = r.get("turn")
                if tid is not None and tid not in turn_idx:
                    turn_idx[tid] = len(turn_order)
                    turn_order.append(tid)
                ev = r.get("event")
                if ev == "PreToolUse":
                    tot += 1
                    if r.get("turn") == turn_id:
                        t_calls += 1
                elif ev == "hook_fire":
                    i = turn_idx.get(r.get("turn"))
                    if i is not None:
                        last_fire[r.get("rule")] = i
                        last_fire_turn[r.get("rule")] = r.get("turn")
    except Exception:
        pass
    return t_calls, tot, turn_order, last_fire, last_fire_turn


def _turn_gap(a, b):
    """turn_id b 在 a 之后几 turn（整数 id 精确，非整数退化 1）。a 是账本里已知的
    上次触发 turn，b 是当前 turn。"""
    try:
        return max(0, int(b) - int(a))
    except (TypeError, ValueError):
        return 1


def cooled_down(last_fire, turn_order, rule_id, turn_id, cooldown_turns,
                last_fire_turn=None):
    """自上次触发后经过的 turn 数 < N → 冷却中。N=1 = 每 turn 最多一次；N=2 =
    触发后跳过 1 个 turn 再放行。
    实现要点：fire 入账发生在 main() 里，本函数看到的是"入账前"的账本；且没触发
    也没工具调用的 turn 完全不入账（冷却吞掉的 turn 不留痕），turn_order 只含
    "有账可记"的 turn。因此：
    - 当前 turn 已入账：cur = 它的 0 起 index，i = last_fire 的 0 起 index，
      (cur - i) < N 即冷却；
    - 当前 turn 未入账（常见：上一 turn 触发了但中间 turn 全被吞）：用整数 turn_id
      的差值（DSH 生产 turn_id = String(lastTurn) 是整数序号）算"经过 turn 数"，
      非整数 id 退化按 1 turn 计；
    - 同 turn 内第二次评估（last_fire_turn == turn_id）一律冷却：入账前 cur-i 恒 0，
      没有这一行 N=1 会漏掉同 turn 重复触发；
    - turn_id 缺失（SessionStart 无 turn）时不做冷却，否则 None 永不入账会让
      "新会话"被旧账本误判成冷却中。"""
    if turn_id is None:
        return False
    if last_fire_turn is not None and last_fire_turn.get(rule_id) == turn_id:
        return True
    i = last_fire.get(rule_id)
    if i is None:
        return False
    if turn_id in turn_order:
        cur = turn_order.index(turn_id)
    else:
        cur = _turn_gap(turn_order[i] if i < len(turn_order) else turn_order[-1] if turn_order else turn_id,
                        turn_id)
    return cur < int(cooldown_turns)


# ---------- 向量（离线特征哈希，免费；可换真实 embedder） ----------

def _hash_vec(text, dims, ngram):
    v = [0.0] * dims
    s = str(text or "").lower()
    if len(s) < ngram:
        s = s.ljust(ngram, "\0")
    for i in range(len(s) - ngram + 1):
        g = s[i:i + ngram]
        # 确定性 64-bit（hashlib；内置 hash() 有进程盐，跨进程不稳定）
        h = int.from_bytes(hashlib.md5(g.encode("utf-8")).digest()[:8], "little")
        idx = h % dims
        sign = 1.0 if (h >> 31) & 1 == 0 else -1.0
        v[idx] += sign
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n > 0 else v


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def anchor_vectors(anchors):
    dims = int(anchors.get("dims", 256))
    ngram = int(anchors.get("ngram", 3))
    out = {}
    for d in anchors.get("domains", []):
        name = d.get("domain")
        if not name:
            continue
        if d.get("vector"):
            out[name] = d["vector"]
        else:
            # 每个关键词单独哈希再平均（拼接会把边界 n-gram 混进噪声）


[assistant • bash]
{"command":"cd /Users/a1-6/Desktop/workspace && sed -n '200,420p' .hooks/engine.py && echo \"===== hooks.json 接线 =====\" && cat .codex/hooks.json 2>/dev/null && echo \"===== TEST-RESULTS.md 尾部 =====\" && tail -30 .hooks/TEST-RESULTS.md && echo \"===== state 目录 =====\" && ls -la .hooks/state/ && head -3 .hooks/state/*.jsonl 2>/dev/null | head -20","description":"读 engine.py 谓词/主流程 + hooks 接线 + 测试结果"}

[tool • bash]
            # 每个关键词单独哈希再平均（拼接会把边界 n-gram 混进噪声）
            vecs = [_hash_vec(str(k).lower(), dims, ngram) for k in d.get("keywords", []) if str(k)]
            out[name] = [sum(x) / len(vecs) for x in zip(*vecs)] if vecs else _hash_vec("", dims, ngram)
    return out, dims, ngram


# ---------- 谓词 ----------

def match_text(seam, payload):
    """按缝取触发文本。Stop/SessionStart 无可靠文本 → 只能 metric/always。"""
    if seam == "UserPromptSubmit":
        return str(payload.get("prompt") or "")
    if seam in ("PreToolUse", "PostToolUse"):
        parts = [str(payload.get("tool_name") or "")]
        ti = payload.get("tool_input") or {}
        if isinstance(ti, dict):
            for k in ("command", "file_path", "path"):
                if ti.get(k):
                    parts.append(str(ti[k]))
        else:
            parts.append(str(ti))
        if seam == "PostToolUse":
            parts.append(str(payload.get("tool_response") or "")[:4000])
        return "\n".join(p for p in parts if p)
    return ""


def pred_always(spec, ctx):
    return True


def pred_keyword(spec, ctx):
    text = ctx["text"]
    pats = spec.get("any") or spec.get("all") or []
    if not pats:
        return False
    if "max_len" in spec and len(text) > int(spec["max_len"]):
        return False
    if "min_len" in spec and len(text) < int(spec["min_len"]):
        return False
    flags = re.IGNORECASE if spec.get("case_insensitive", True) else 0
    compiled = []
    for p in pats:
        compiled.append(re.compile(p, flags) if spec.get("regex") else re.compile(re.escape(str(p)), flags))
    if spec.get("all"):
        return all(rx.search(text) for rx in compiled)
    return any(rx.search(text) for rx in compiled)


def pred_metric(spec, ctx):
    v = ctx["metrics"].get(spec.get("field", ""), 0)
    n = spec.get("value", 0)
    op = spec.get("op", ">=")
    return {"<": v < n, "<=": v <= n, ">": v > n, ">=": v >= n, "==": v == n, "!=": v != n}.get(op, False)


def pred_vector(spec, ctx):
    th = float(spec.get("threshold", 0.18))
    av = ctx["anchor_vecs"]
    scope = spec.get("domain")
    text_v = _hash_vec(ctx["text"], ctx["dims"], ctx["ngram"])
    best, best_name = 0.0, None
    for name, vec in av.items():
        if scope and name != scope:
            continue
        c = cosine(text_v, vec)
        log_err(f"  [vector] {name}: {c:.4f}")
        if c > best:
            best, best_name = c, name
    if best_name:
        ctx["debug_best_domain"] = (best_name, best)
    return best >= th


def pred_lexicon(spec, ctx):
    """领域词表匹配（确定性、可校准）：文本命中的 distinct 锚关键词数 >= min_hits 即触发，取最高分 domain。
    256 维特征哈希余弦经测量对短中文无区分度（噪声 0.22 > 信号 0.14），故领域触发默认用本谓词；
    vector 谓词保留给将来真实 embedder（anchors.json 的 vector 字段）。"""
    th = int(spec.get("min_hits", 2))
    scope = spec.get("domain")
    text = str(ctx["text"] or "").lower()
    anchors = load_json(ANCHORS_PATH, {"domains": []})
    best, best_name = 0, None
    for d in anchors.get("domains", []):
        name = d.get("domain")
        if not name or (scope and name != scope):
            continue
        kws = [str(k).lower() for k in d.get("keywords", []) if str(k)]
        hits = sum(1 for k in kws if k in text)
        log_err(f"  [lexicon] {name}: {hits}/{len(kws)}")
        if hits > best:
            best, best_name = hits, name
    if best_name:
        ctx["debug_best_domain"] = (best_name, best)
    return best >= th


def pred_judge(spec, ctx):
    """外部 LLM 裁判（可选）。judge_cmd 读到 stdin 文本，stdout 以 expect 开头 = 触发。默认不启用。"""
    cmd = spec.get("judge_cmd")
    if not cmd:
        return False
    try:
        r = subprocess.run(cmd, shell=True, input=ctx["text"][:4000], capture_output=True,
                           text=True, timeout=float(spec.get("timeout", 30)))
        out = r.stdout.strip()
        log_err(f"  [judge] exit={r.returncode} out={out[:120]!r}")
        return out.upper().startswith(str(spec.get("expect", "1")).upper())
    except Exception as e:
        log_err(f"  [judge] error: {e}")
        return False


PREDICATES = {
    "always": pred_always,
    "keyword": pred_keyword,
    "metric": pred_metric,
    "vector": pred_vector,
    "lexicon": pred_lexicon,
    "judge": pred_judge,
}


def eval_trigger(trigger, ctx):
    specs = trigger if isinstance(trigger, list) else [trigger]
    for spec in specs:  # 级联 OR，短路，按配置顺序（模型应把便宜的放前面）
        t = (spec or {}).get("type", "always")
        fn = PREDICATES.get(t)
        if fn is None:
            log_err(f"  [trigger] unknown type: {t}")
            continue
        try:
            if fn(spec, ctx):
                return True, t
        except Exception as e:
            log_err(f"  [trigger] {t} error: {e}")
    return False, None


# ---------- main ----------

def main():
    seam = sys.argv[1] if len(sys.argv) > 1 else ""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    rules_doc = load_json(RULES_PATH, {"rules": []})
    config = rules_doc.get("config", {}) or {}
    anchors = load_json(ANCHORS_PATH, {"dims": 256, "ngram": 3, "domains": []})
    anchor_vecs, dims, ngram = anchor_vectors(anchors)

    session_id = payload.get("session_id") or "unknown"
    turn_id = payload.get("turn_id")
    t_calls, tot_calls, turn_order, last_fire, last_fire_turn = ledger_scan(session_id, turn_id)
    metrics = {"tool_calls_this_turn": t_calls, "tool_calls_total": tot_calls,
               "turn_id": str(turn_id) if turn_id is not None else ""}

    text = match_text(seam, payload)
    ctx = {"text": text, "payload": payload, "seam": seam, "metrics": metrics,
           "anchor_vecs": anchor_vecs, "dims": dims, "ngram": ngram}

    injects, denies = [], []
    for rule in rules_doc.get("rules", []):
        if not rule.get("enabled", True) or rule.get("seam") != seam:
            continue
        rid = rule.get("id", "?")
        ok, which = eval_trigger(rule.get("trigger", {"type": "always"}), ctx)
        if not ok:
            continue
        if cooled_down(last_fire, turn_order, rid, turn_id,
                       rule.get("cooldown_turns", 1), last_fire_turn):
            log_err(f"[{rid}] fired via {which} but cooled down")
            continue
        action = rule.get("action", {})
        log_err(f"[{rid}] FIRED via {which}")
        ledger_append(session_id, {"event": "hook_fire", "rule": rid, "turn": turn_id,
                                   "via": which, "ts": time.time()})
        if action.get("inject"):
            injects.append(render(action["inject"], config))
        if action.get("deny"):
            denies.append(render(action["deny"], config))

    # 记录工具调用（供 metric 谓词跨事件累积）
    if seam == "PreToolUse":
        ledger_append(session_id, {"event": "PreToolUse", "turn": turn_id,
                                   "tool": payload.get("tool_name"), "ts": time.time()})

    out = {}
    if denies:
        out = {"decision": "deny", "reason": "\n".join(denies)}
    if injects:
        out["additionalContext"] = "\n\n".join(injects)
    if out:
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(os.path.join(STATE_DIR, "engine-error.log"), "a", encoding="utf-8") as f:
                f.write(f"{time.time()} {e!r}\n")
        except Exception:
            pass
        sys.exit(0)
===== hooks.json 接线 =====
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python3 .hooks/engine.py SessionStart", "timeout": 10 } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python3 .hooks/engine.py UserPromptSubmit", "timeout": 10 } ] }
    ],
    "PreToolUse": [
      { "hooks": [ { "type": "command", "command": "python3 .hooks/engine.py PreToolUse", "timeout": 10 } ] }
    ],
    "PostToolUse": [
      { "hooks": [ { "type": "command", "command": "python3 .hooks/engine.py PostToolUse", "timeout": 10 } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python3 .hooks/engine.py Stop", "timeout": 10 } ] }
    ]
  }
}
===== TEST-RESULTS.md 尾部 =====
| cd=1 同 turn 第二次被吞（irreversible-op-guard） | PASS | 同 turn 第二次 `rm -rf` → 无输出（first deny, second null） |
| 同 turn 第二次 Stop 被吞（overthink-backstop, cd2） | PASS | 9 次调用后 Stop#1 deny，Stop#2 同 turn 空输出 |

## max_len

| 用例 | 结果 | 证据 |
|---|---|---|
| 150 字符 + "？" 的长 prompt 不触发 l0 关键词谓词 | PASS | ac 无 "⚡ L0 检测" 行（thinking-budget-frame 的 always 谓词无 max_len，仍会注入，属预期；测试只断言 L0 行） |

## 异常输入

| 用例 | 结果 | 证据 |
|---|---|---|
| 空 stdin | PASS | exit 0，无输出，stderr 空 |
| 坏 JSON stdin（`{not json`） | PASS | exit 0，无输出 |
| 未知 seam（`NoSuchSeam`） | PASS | exit 0 不崩溃 |
| HOOK_DEBUG=1 stderr 诊断 | PASS | stderr 含 `[overthink-guard-l0] FIRED via keyword` / `[thinking-budget-frame] FIRED via always` 及 lexicon 命中计数 |

## 本次修复的 bug（engine.py，改后快照 /tmp/engine.py.bak-20261019_021319；修前快照 /tmp/engine.py.bak-20261019_010319 已丢失）

1. **cooldown 同 turn 绕过 + 跨 turn 语义错**（cooled_down）：
   - 根因：fire 入账在 main() 里发生在 cooled_down 之后，进程看到的是"入账前"账本；且被冷却吞掉的 turn 不产生任何账本行，turn_order 只含"有账可记"的 turn，用 `len(turn_order)` 或 `index` 无法区分 1-gap 与 2-gap（t2 时 order 仍只有 [t0]）。
   - 修法：新增 `_turn_gap(a,b)=max(0,int(b)-int(a))`（非整数退化 1）；cur 取"已入账则 index，未入账则 `_turn_gap(order[i], turn_id)`"；另加 `last_fire_turn == turn_id → True` 兜住同 turn 第二次（入账前 cur-i 恒 0，N=1 会漏）。turn_id 缺失（SessionStart）不冷却，否则 None 永不入账会让新会话被旧账本误判冷却中。
2. **turn_id=None 时 len(turn_order) 对非空账本总 ≥ i → 新会话误判永远冷却**（同一条修法的分支）。
3. rules.json 配套（改前备份 /tmp/rules.json.bak-20261019_021319）：overthink-guard-l0 cooldown 1→2（让"连续两 turn 第二次被吞"可测）；session-orientation 加 cooldown_turns:2。

## 已知限制（DSH 端，非引擎 bug）

- **DSH 挂载（2026-10-19 已闭环）**：lead 已在活跃 web profile 的 `~/Library/Application Support/dsh-desktop/harness/profiles/web/cordis.patch.yml` 写入 `@deepseek-ai/dsh-hooks-codex` 条目（config: configPath `./workspace/.codex/hooks.json`，model `qwen3.8-27b-w8a16`），**待用户重启 DSH 后生效**。此前排查的 `~/.dsh/profiles/desktop/` 是旧 CLI profile，非活跃。
- 桥接语义（dsh-hooks-codex v0.2.0-rc.2）：PreToolUse 忽略 additionalContext（仅阻塞生效）；非 shell 工具 tool_input 缩为 {command}（其他工具 command=""）；Stop 的 last_assistant_message 恒 null、无条件 deny 会死循环（deny→steer 强制再走一步）；SessionStart detached 执行可能错过首请求；turn_id 为内部整数序号。
===== state 目录 =====
total 16
drwxr-xr-x@ 4 a1-6  staff  128 Oct 20 00:10 .
drwxr-xr-x@ 9 a1-6  staff  288 Oct 20 02:26 ..
-rw-r--r--@ 1 a1-6  staff  110 Oct 19 23:12 test-manual.jsonl
-rw-r--r--@ 1 a1-6  staff  110 Oct 20 00:10 test.jsonl
==> .hooks/state/test-manual.jsonl <==
{"event": "hook_fire", "rule": "session-orientation", "turn": null, "via": "always", "ts": 1792422733.202045}

==> .hooks/state/test.jsonl <==
{"event": "hook_fire", "rule": "session-orientation", "turn": null, "via": "always", "ts": 1792426218.408585}


[assistant • bash]
{"command":"cd \"/Applications/DSH Desktop.app/Contents/Resources/app.asar\" 2>/dev/null && ls node_modules/@deepseek-ai/ 2>/dev/null | head -40 && echo \"===== 找 plugin/hook 相关文档 =====\" && ls | head -30","description":"列 DSH asar 内 @deepseek-ai 包清单"}

[tool • bash]
(no output)
[exit code: 1]