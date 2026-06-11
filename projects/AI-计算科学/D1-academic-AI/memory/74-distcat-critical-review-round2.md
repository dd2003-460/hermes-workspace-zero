# DistCat 第二轮副脑审查结果

> **创建**: iteration 74
> **来源**: Subagent a130b0b83a55e4584 审查
> **类型**: 关键审查 — Theorem 3.1 漏洞修复

## 最关键的弱点

**Theorem 3.1 (Fisher-Rao 普适性) 被攻击**: EMRI 和 D1-grav-waves 不是指数族，而是光滑参数化的洛伦兹度量族。

### 两层漏洞

**Layer 1**: EMRI (Dehnen 度规) 和 D1-grav-waves (AQFT 态) 没有指数族结构 — 没有 p(x|θ)，没有似然函数，没有 KL 散度从数据导出。

**Layer 2**: 唯一性证明机制 (DPI, 充分性, KL 二次展开) 不适用于 EMRI 的动力学不变量。Lyapunov 指数是**动力学不变量**，不是统计泛函。

### 修复方案 (已实施)

1. 降级 Theorem 3.1 为 "Fisher-Rao 统计子类优性定理"
2. 增加非统计例子的"标准预距离"分类表
3. 统一原理改为: "标准预距离是使自然变换 η: δ→Γ 成为局部等距的唯一度量"
4. 统计模型 → Fisher-Rao (Amari/Cencov)
5. 非统计模型 → 诱导黎曼度量

###  surviving content

- 2-范畴形式化 — 保留
- 距离导出原理 δ=Φ(Γ) — 保留
- 所有显式物理计算 — 保留
- Fisher-Rao 对 D16+D24 和 Bayesian — 保留 (真正的统计模型)
- D26 特征值空间欧氏距离 — 保留 (正交不变性)

## 文件更新
- papers/DISTCAT-optimal-distance-export.md: Theorem 3.1 降级 + 讨论区修复
- 本文件存档
