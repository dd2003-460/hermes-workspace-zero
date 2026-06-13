# Cross-Paper Cross-Reference Implementation

**来源**: 跨论文综合评审副脑质询 P1修复
**状态**: 交叉引用100%完成; 迭代29新增模型比较

## 完成的修复

### Chimera (chimera-stable-attractors/)
- 新增3篇intra-project引用: S12-1 (co-discovery phase transition), S17-1 (semantic space geometry), S18-1 (computational complexity routing)
- Discussion Broader Implications新增: "Unified coexistence classification" -- H1 classification与全局理论框架的统一
- 编译通过: 20p, 356KB, 0 errors

### S18-1 (s18-1-kolmogorov-router/)
- 新增2篇intra-project引用: Chimera (H1 classification, basin geometry), S12-1 (cluster detection methodology)
- Related Work新增: "Intra-project connections" paragraph
- 迭代28修正: "formally equivalent to MDL" -> "formally analogous to MDL"; abstract "phase transition" -> "sharp crossover"
- 编译通过: 11p, 502KB, 0 errors

### S12-1 (s12-1-co-discovery-phase-transition/) -- 迭代25-29
- 新增2篇intra-project引用: Chimera (H1 classification, basin geometry), S18-1 (computational complexity routing, phase transition formalism)
- 新增subsection "Connection to Coexisting State Classification": sigma_i与H1分类体系形式类比
- 新增subsection "Connection to Computational Complexity Routing": 聚类检测与复杂度路由方法论类比
- 迭代29: Discussion新增模型比较表(Phase Transition R2=0.981 vs Logistic R2=0.889 vs Exponential R2=0.661)
- 迭代29: Conclusion更新，加入AIC比较结果描述
- 编译通过: 9p, 209KB, 0 undefined references

### S17-1 (S17-1-semantic-space-geometry/)
- 迭代26: 新增3篇intra-project引用 (Chimera basin-geometry, discovery-clustering, complexity-routing)
- 迭代27: 新增4篇关键文献 (Nickel/Kiela 2017, Ganea 2018, Amari 1985, Peters 2016)
- 迭代27: 曲率公式修正: "曲率=空间黎曼曲率" -> "曲率=路径弯曲程度(path straightness)"
- 迭代27: "形式同构" -> "形式类比"
- 编译: 需Mac (fontset=mac, TinyTeX缺unihei5c)

## 待完成的修复
- S17-1: 需Mac重编PDF (fontset=mac)
- P2: S17-1 "pilot study" 语言降级 (n=14 concept pairs)

## 系统性问题状态
| 问题 | 状态 |
|------|------|
| P0: S17-1曲率符号 | 源文件修复完成, 需Mac重编 |
| P1: 零交叉引用 | 100%完成 (Chimera+S18-1+S12-1+S17-1双向交叉引用) |
| P1: 相变术语不一致 | S18-1已修正(abstract crossover); 其余论文无此问题 |
| P1: 投稿策略 | 跳过 (作者确认阻塞) |
| P2: S17-1 pilot语言 | 未开始 |
| P1: S18-1 UCB/Thompson基线 | 迭代29 dispatch sub-brain |
| P2: S12-1 non-AI控制组 | 需新数据收集 |
