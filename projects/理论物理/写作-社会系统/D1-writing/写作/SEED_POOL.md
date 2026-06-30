# Writing Seed Pool — 影响力燃料

来源：IC_K 论文 open questions + 副脑建议 + 自主扩展
最后更新：2026-04-02 Round 10

## 评估标准
1. **洞见密度**：是否有新观点？还是复述已知？
2. **受众价值**：能帮到谁？谁会读？
3. **永生目标指向**：是否服务于学术平台构建？
4. **自主可行性**：不需要用户决策即可推进？

---

## 🌱 Tier A: 高优先级种子（有内容，可立即起草）

### A1: "The Direct Sum Mystery in Kolmogorov Complexity"
- **来源**: IC_K 论文 Open Problem #1
- **形式**: 博客 / 短论文
- **受众**: TCS 社区、Kolmogorov 复杂度研究者
- **角度**: O(n log n) 间隙是技术困难还是本质限制？为什么 Kolmogorov 框架下 Direct Sum 不能像 Shannon 框架一样紧？
- **自主可行性**: ✅ 全部基于已有分析
- **状态**: 📝 草稿完成 (~3000 words, 2026-04-04)
- **文件**: `a1_direct_sum_draft.md`

### A2: "Why Average-Case Analysis Isn't Enough: A Kolmogorov Perspective"
- **来源**: IC_K vs IC 的哲学对比
- **形式**: 博客
- **受众**: ML/TCS 交叉社区
- **角度**: inf_μ IC = 0 的反直觉结果 → 平均情况分析的结构性缺陷 → worst-case 分布自由框架的必要性
- **自主可行性**: ✅ 完全自包含
- **预计**: 1500-2500 words

### A3: "IC_K ≠ inf IC: When Averaging Destroys Information"
- **来源**: IC_K 论文 Theorem 3 + 推论
- **形式**: Twitter thread / 短博客
- **受众**: 信息论 + 通信复杂度社区
- **角度**: 单点分布退化的反直觉 → "为什么不能简单取 inf over distributions"
- **自主可行性**: ✅
- **预计**: 8-12 tweets 或 1000 words

---

## 🌿 Tier B: 中优先级种子（需要额外研究但方向明确）

### B1: "Minimax Duality: IC vs IC_K"
- **来源**: IC_K 论文 Open Problem #7
- **形式**: 博客 / 论文
- **受众**: TCS 博弈论交叉
- **角度**: IC = sup_μ inf_π vs IC_K = inf_π sup_{x,y} 的 reversed quantifier → von Neumann minimax 定理的适用性
- **依赖**: 需要更多数学分析
- **预计**: 3000+ words（含证明）

### B2: "Randomized Information Complexity: What Changes?"
- **来源**: IC_K 论文 Open Problem #3
- **形式**: 博客
- **受众**: 通信复杂度社区
- **角度**: IC_K^R(EQ) = O(1) << IC_K(EQ) = Θ(log n) → 随机化如何改变信息复杂度
- **依赖**: 需要更多实例分析
- **预计**: 2000 words

### B3: "Computability of Information Complexity"
- **来源**: IC_K 论文 Open Problem #6
- **形式**: 博客
- **受众**: 可计算性 + TCS 社区
- **角度**: IC_K 的 Turing degree → 不可计算性 vs 可近似性
- **依赖**: 需要深入可计算性理论
- **预计**: 2000 words

---

## 🌳 Tier C: 长期种子（跨领域 / meta / 需要用户方向）

### C1: "Academic Writing with AI: An Honest Account"
- **来源**: 副脑建议
- **形式**: 博客
- **受众**: 学术界 + AI 社区
- **角度**: 用 AI 写 IC_K 论文的真实流程、成功/失败、质量判断
- **依赖**: 需要用户对 AI 辅助写作的个人视角
- **预计**: 2000 words

### C2: "From Shannon to Kolmogorov: Bridging Two Information Theories"
- **来源**: 副脑建议 + 论文 Discussion
- **形式**: 科普长文
- **受众**: 广泛 CS/ML 社区
- **角度**: Shannon 信息论 vs Kolmogorov 复杂度的历史、区别、统一尝试
- **依赖**: 需要大量科普写作
- **预计**: 4000+ words

### C3: 用户种子想法
- **来源**: 待用户回答 "你最近在反复思考什么？"
- **形式**: 未知
- **依赖**: 用户输入

---

## 下一步行动
1. 从 Tier A 中选一个开始起草（推荐 A2: 平均情况分析 — 最独立、受众最广）
2. 每 2 周评估一次种子池优先级
3. 发布后收集反馈，更新种子池
