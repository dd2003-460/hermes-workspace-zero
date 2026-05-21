# DistCat 合并方案 v5

## 背景

当前有 4 篇 arXiv-ready 论文：
1. D1-grav-waves (v4): HD 相关性作为 AQFT 自然变换
2. DistCat (v3): 2-范畴距离导出框架
3. BayesFrame (v1): |sin(4θ)| 方向偏差
4. EMRI (v0): D26 共振放大在 DM 晕中的实现

副脑 (iter 139) 指出：**DistCat 是元论文，已包含 grav-waves (Example 1), EMRI (Example 5), BayesFrame (Example 3) 作为特例。分开提交造成 ~30-40% 重复。**

## 方案 A：合并为 DistCat v5 (Signature Paper)

**目标**: 将 grav-waves 和 EMRI 的核心定理完整整合入 DistCat，形成一篇 25-30 页的 signature paper，目标期刊 JAMS/CMH (math.CT)。

### 合并后的论文结构

```
DistCat v5 (25-30 pages)
├── 1. 引言 (3p)
│   ├── 距离导出原理的统一观点
│   ├── 2-范畴框架概述
│   └── 5 个跨学科特例的速览
├── 2. 形式化定义 (5p)
│   ├── 2-范畴 DistCat 的严格定义
│   ├── 2-函子 D: DistCat → Met
│   ├── 观测不可行性定理
│   └── 距离等价类
├── 3. 例 1: AQFT + PTA (4p)
│   ├── Hellings-Downs 作为自然变换
│   ├── 源判别定理 (TV distance)
│   └── 各向同性定理
├── 4. 例 2: 统计模型比较 (2p)
│   └── Fisher 信息几何 + 语义测地线
├── 5. 例 3: 贝叶斯推断 (2p)
│   └── Fisher-Rao 距离 + 边缘化
├── 6. 例 4: 控制理论共振 (2p)
│   └── D26 共振放大
├── 7. 例 5: EMRI 混沌 (4p)
│   ├── D26↔EMRI 映射
│   ├── KAM 标度律证明
│   └── 观测桥梁 (GW 频谱)
├── 8. 跨框架距离等价 (2p)
│   └── D1 vs EMRI, D26 vs EMRI 等
├── 9. 讨论与展望 (1p)
└── 参考文献 (1p)
```

### 工作量估计

- 需要新增约 10 页内容 (grav-waves 的完整定理 + EMRI 的完整证明)
- 当前 DistCat v3 为 14p，需要增加 ~50% 内容
- 估计工时: ~8h

### 风险

- 论文长度增加可能导致 math.CT 社区的耐心下降
- grav-waves 定理的 AQFT 细节与 EMRI 的 GR 细节可能使论文过于分散
- 目标期刊选择: JAMS (too high) / CMH (appropriate) / CQG (too applied)

## 方案 B：DistCat 保持不变 + 交叉引用 (推荐短期方案)

**策略**:
1. DistCat v4 (math.CT) — 保持现有 14p，强化 2-范畴定理
2. grav-waves v5 (gr-qc) — 在引言中引用 DistCat，强调物理预测
3. BayesFrame v1 (q-bio.NC) — 独立提交
4. EMRI v0 (gr-qc) — 在引言中引用 DistCat

**优点**:
- 4 篇论文均可立即提交，4 个 arXiv IDs
- 物理社区的读者可能不关心 DistCat 的范畴细节
- BayesFrame 是完全独立的领域

**缺点**:
- DistCat 和其他论文之间存在 ~30% 内容重复
- 未来引用可能出现自引循环

## 方案 C：混合方案 (推荐长期方案)

**策略**:
1. 立即提交 DistCat v4 (math.CT) + BayesFrame v1 (q-bio.NC) + D40 (cs.AI)
2. grav-waves 和 EMRI 暂存为 preprint，等待 DistCat v5 合并
3. DistCat v5 作为"unified framework"论文，整合所有 4 个特例

**优点**:
- 3 篇论文立即获得 arXiv IDs
- grav-waves + EMRI 在 DistCat v5 中作为定理获得更高引用价值
- DistCat v5 成为 signature paper

## 推荐: 方案 C

理由：
1. 用户目标: academic output (0.4) — 3 篇论文立即提交优于等待
2. DistCat v5 作为 signature paper 需要更多时间打磨
3. grav-waves + EMRI 在 DistCat 框架下获得更强的理论地位

## DistCat v5 规划 (远期)

- [ ] 将 grav-waves 的 HD 自然变换定理完整导入 DistCat (Sec 3)
- [ ] 将 EMRI 的 KAM 标度律证明完整导入 DistCat (Sec 7)
- [ ] 添加 Bridge paper 作为 "未来展望" (Sec 9)
- [ ] 2-范畴完备性定理 (新)
- [ ] 目标期刊: CMH 或 JHEP (math-ph section)
