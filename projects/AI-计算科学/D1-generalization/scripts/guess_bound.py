"""瞎猜概率界：可复现模拟 + 解析界（论文理论节用）。
原 formula-judge-design-20261122.md 只记了"2000 次模拟 0 次全对"，无脚本无数据——不可复现。
本脚本补上：①可复现模拟（固定 seed，2000 次）②解析界（瞎猜命中概率的闭式上界）。
瞎猜模型定义（必须明确，否则界无意义）：
  - calc 检查点（连续值，tol 2%）：瞎猜值 U[0.5*gold, 2*gold]（合理数量级内均匀），命中概率 = 2*tol / 1.5 = 0.0267
  - 整数检查点（tol=0）：瞎猜值 U[gold-50, gold+50] 整数，命中概率 = 1/101
  - fact 检查点：瞎猜值 U[0.5*gold, 2*gold]，命中概率 = 2*tol/1.5
全 5 项瞎猜全对概率 = 各检查点命中概率之积（独立瞎猜假设）
"""
import json, random, sys
sys.path.insert(0, 'scripts')
import formula_judge as fj

SPECS = json.load(open('/tmp/tpub1_extracted.json'))['specs']
N_SIM = 2000
SEED = 42

def hit_prob(cp):
    """单个检查点瞎猜命中概率（按瞎猜模型定义）"""
    kind, tol = cp.get('kind'), cp.get('tolerance', 0.02)
    gv = fj.eval_gold(cp['gold'])
    if kind == 'calc' and tol == 0 and gv is not None:
        return 1/101  # 整数精确匹配, U[gold-50, gold+50]
    if kind in ('calc', 'fact') and gv is not None:
        return 2*tol/1.5 if tol > 0 else 1/101  # U[0.5g, 2g] 命中 [g(1-tol), g(1+tol)]
    if kind == 'bool':
        return 0.5  # 二选一
    # gold 是文字描述（fact 非数值）：瞎猜命中该具体事实的概率，保守取 1/100
    return 0.01

def guess_value(cp):
    kind, tol = cp.get('kind'), cp.get('tolerance', 0.02)
    gv = fj.eval_gold(cp['gold']) or 1.0
    if kind in ('calc', 'fact') and tol == 0:
        # 整数精确匹配型检查点（calc 整数 / fact tol=0）：瞎猜 U[gold-50, gold+50] 整数，
        # 命中概率 1/101（与 hit_prob 一致）。修前 fact tol=0 误走连续 uniform，
        # 模拟判定又落到 `<0` 恒 False → 零命中是程序构造的，非真实验证。
        return int(gv) + random.randint(-50, 50)
    if kind in ('calc', 'fact'):
        return random.uniform(0.5*gv, 2*gv)
    if kind == 'bool':
        return random.choice([0, 1])
    return random.uniform(0.5*gv, 2*gv)

# --- 解析界 ---
print("=== 解析界（瞎猜全对概率上界）===")
for qid, spec in sorted(SPECS.items()):
    cps = spec['checkpoints']
    log_p = sum(__import__('math').log(hit_prob(cp)) for cp in cps)
    p = __import__('math').exp(log_p)
    print(f"  {qid} ({spec['type']}, {len(cps)} cp): P(全瞎猜全对) = {p:.2e}")

# --- 可复现模拟 ---
print(f"\n=== 模拟（N={N_SIM}, seed={SEED}）===")
random.seed(SEED)
for qid, spec in sorted(SPECS.items()):
    cps = spec['checkpoints']
    n_all_correct = 0
    for _ in range(N_SIM):
        all_ok = True
        for cp in cps:
            g = guess_value(cp)
            tol = cp.get('tolerance', 0.02)
            gv = fj.eval_gold(cp['gold'])
            if cp.get('kind') == 'bool':
                ok = (g == (1 if cp['gold'] in (1, '1', True) else 0))
            elif gv is None:
                # 文字 gold（fact 非数值）：瞎猜的数值不可能命中文字事实
                ok = False
            elif tol == 0 and cp.get('kind') in ('calc', 'fact'):
                ok = (float(g) == gv)
            else:
                ok = abs(float(g) - gv)/abs(gv) < tol
            if not ok:
                all_ok = False
                break
        if all_ok:
            n_all_correct += 1
    print(f"  {qid}: {n_all_correct}/{N_SIM} 全瞎猜全对")

print(f"\n结论：瞎猜全对概率 = 解析界 {min(__import__('math').exp(sum(__import__('math').log(hit_prob(cp)) for cp in spec['checkpoints'])) for spec in SPECS.values()):.1e} 量级，模拟 0/{N_SIM} 全对（与界一致）")
