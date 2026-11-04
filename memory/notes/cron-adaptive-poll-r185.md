# origin: ai — Cron 自适应轮询 (r185)

## 动机
成璐要求：cron 间隔缩短到 500s 以内随机数 + 排队检测（在跑就跳过）+ 不断缩短间隔轮询。

## 实现
**修改文件**: `~/.hermes/hermes-agent/cron/jobs.py` (备份 `/tmp/jobs.py.bak-20261102`)

### Patch #1 — 排队守卫 (`_evaluate_due_job` ~L3217)
```python
if schedule.kind in {"cron", "interval"} and job.get("adaptive_poll"):
    try:
        from cron.scheduler import is_job_running as _isjr
        if _isjr(str(job.get("id"))):
            return False  # 还在跑，跳过本次触发
    except Exception:
        pass  # fail-open
```

### Patch #2 — 随机间隔 (`_advance_after_run` ~L2405)
```python
if job.get("adaptive_poll") and kind in {"cron", "interval"} and job["next_run_at"] is not None:
    _poll_secs = random.randint(60, 500)
    _now_dt = _parse_aware(now) or _hermes_now()
    job["next_run_at"] = (_now_dt + timedelta(seconds=_poll_secs)).isoformat()
```

### Job 标记
`~/.hermes/cron/jobs.json` → job `8d0311e989fc` 加 `adaptive_poll: True`

## 测试
- 排队守卫: mock running → 正确跳过; mock not running → 正常触发 ✅
- 随机间隔: 模拟跑完一次 → 实际算出 497s (范围 60-500) ✅
- 语法检查: `import cron` OK ✅
- 未影响其他 job: 只有带 `adaptive_poll` 标记的才走新逻辑 ✅

## 状态（2026-11-04 更新）
- **代码已落地**，gateway 需重启后生效
- **⚠️ 已禁用（r29x, 2026-11-04）**：成璐反馈 ~15min 一轮重复播报同内容。已从 `jobs.json` 移除 job `8d0311e989fc` 的 `adaptive_poll` 字段（备份 `jobs.json.bak-adaptive-poll-fix`），该 job enabled=false。随机 60-500s 轮询对"监督者"型 cron 太激进——每轮都重读 stop-hook 快照 + goal 模板再播报，内容高度重复。**教训：adaptive_poll 只适合真正高频事件驱动的场景；长周期监控用固定 interval + [SILENT] 抑制即可。**
- **过渡方案**: interval 已从 30m → 5m (cronjob_manage update)，即使自适应没生效也快了 6 倍

## 相关文件
- `~/.hermes/scripts/wx-push.py` — WeChat 推送（无参数读 /tmp/wx-msg.txt）
- `~/.hermes/config.yaml` — pre_llm_call hooks (inject-rules.sh, hook.py, auto_continue_hook.py)
- `tools/stage-gate/stage_gate/adapters/auto_continue_hook.py` — stop-hook 注入器
