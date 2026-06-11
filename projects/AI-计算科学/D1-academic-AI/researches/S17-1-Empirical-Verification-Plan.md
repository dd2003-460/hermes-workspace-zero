# S17-1 实证验证方案: 语义空间曲率与测地线假设

**迭代**: 25 (2026-06-09)
**对应TASKS.md任务**: S17-1 测地线不变量 + S17-1 信息论关联
**灵感来源**: Du & Tanaka-Ishii 2405.06321 "Correlation Dimension of Natural Language in a Statistical Manifold"

---

## 假设体系

### 主假设 H0
语义空间（word embedding space）的黎曼度量张量 $g_{ij}$ 非零——语义空间不是欧几里得的，有内在曲率。

### 子假设 H1
概念对之间的语义距离与嵌入空间中的欧氏距离**显著相关**（R² > 0.5），但残差可用曲率解释。

### 子假设 H2
"绕路"路径（不直接相邻的概念序列）与"最短"路径（直接相邻）的信息损失有上限——即测地线近似存在。

---

## 实验设计

### 实验1: 语义空间曲率测量

**输入**: 预训练BERT/W2V embeddings

**步骤**:
1. 从WordNet或WikiWords获取概念层级树（如 "动物 → 哺乳动物 → 狗 → 拉布拉多"）
2. 将概念映射到embedding空间
3. 在局部区域估计Fisher信息度量 $g_{ij}$：
   - 对每个概念 $c$，计算其embeddings的概率分布（通过softmax over vocabulary）
   - $g_{ij}(c) = \mathbb{E}[\partial_i \log p \cdot \partial_j \log p]$
   - 用finite difference近似梯度
4. 计算Riemann曲率张量 $R_{ijkl}$ 和sectional curvature

**预期结果**: 
- 如果H0为真 → sectional curvature显著非零
- 如果H0为假 → sectional curvature接近0

### 实验2: 语义距离-欧氏距离相关性

**输入**: ConceptNet或WordNet的概念对距离标注

**步骤**:
1. 从ConceptNet获取concept pairs及human-annotated semantic similarity scores
2. 计算embeddings中的欧氏距离 $d_{euclidean}$
3. 计算测地线近似距离（using Dijkstra shortest path on k-NN graph）
4. 比较 $d_{euclidean}$ 和 $d_{geodesic}$ 与 human similarity scores的相关系数

**预期结果**:
- 如果H1为真 → $d_{geodesic}$ 与 human similarity的相关系数 > $d_{euclidean}$ 的相关系数
- 预期增益: Spearman rho提升 0.1-0.3

### 实验3: "绕路"路径的信息损失

**输入**: 预训练BERT embeddings

**步骤**:
1. 构建k-NN语义图（k=10）
2. 对随机选择的概念对 (A, B)：
   - 找出最短路径 $P_{short}$（Dijkstra）
   - 找出绕路路径 $P_{detour}$（随机游走，长度 < 2 * |P_short|）
3. 对每条路径计算：
   - 路径的平均曲率 $K_{path} = \frac{1}{|P|} \sum_i K(p_i)$
   - 路径的信息损失 $IL_{path} = H(p_{start}) - H(p_{end})$（使用BERT的hidden state entropy）
4. 比较 $IL_{short}$ 与 $IL_{detour}$

**预期结果**:
- 如果S17-1的"绕路不增加距离"为真 → $IL_{detour} \approx IL_{short}$
- 如果语义空间是欧几里得的 → $IL_{detour} \gg IL_{short}$

---

## 实现方案

### Python脚本结构

```
chimera_lab/s17_semantic_manifold/
├── run_analysis.py          # 主入口
├── embedding_utils.py       # BERT/W2V加载和查询
├── curvature.py             # Fisher信息度量估计 + 曲率计算
├── geodesic.py              # k-NN图 + Dijkstra + path comparison
├── datasets.py              # WordNet/ConceptNet数据加载
└── requirements.txt
```

### 依赖
- torch + transformers (BERT)
- numpy + scipy
- networkx (k-NN图)
- wn (WordNet)

### 预计运行时间
- 实验1: ~5分钟（50个概念，局部曲率估计）
- 实验2: ~10分钟（ConceptNet加载 + 距离计算 + 相关性分析）
- 实验3: ~15分钟（随机路径采样 + 信息损失计算）
- **总计: ~30分钟**

---

## 产出

1. 语义空间curvature的数值估计
2. $d_{euclidean}$ vs $d_{geodesic}$ 的对比图表
3. "绕路"路径vs"最短"路径的信息损失分布
4. 对S17-1假说的支持/反驳结论
