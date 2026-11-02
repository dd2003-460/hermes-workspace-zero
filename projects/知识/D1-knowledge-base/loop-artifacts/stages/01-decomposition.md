# 01-goal-decomposition — KB.1 第6篇教材 note：向量数据库与余弦相似度

## 任务目标（五字段）

【目标】为成璐写第 6 篇教材式 note：向量数据库与余弦相似度。讲清 embedding、余弦相似度、HNSW/ANN、本地方案选型——agent 记忆系统里"检索"这一环到底在算什么、为什么这么算。

【阶段】KB.1（projects/知识/D1-knowledge-base），队列第 6 篇，前 5+ 篇已完成且全过 drift-check。本 goal 走本地直写通道（KB 项目历史先例：Lead 直写，非 arena 外包——单文件写作任务，arena 链路开销不划算）。

【SOP 索引】
- KB README 格式规范：`projects/知识/D1-knowledge-base/README.md`（A 名词表 4 字段 + B 成璐视角段 + L1/L2/L3 分层）
- voice 门禁：`projects/AI-计算科学/D1-persona-align/scripts/drift-check.py`（硬门槛：第一人称≥0.2、句长<55、空话 0）
- 素材锚：decomp T17 rag-vs-longctx gold tree + runs（RAG 域拆解）、memory-benchmarks LoCoMo 实验（agent 记忆检索实测）

【验收标准】（机器可查）
1. `notes/vector-database-cosine-similarity.md` 存在，A 名词表 ≥8 概念，每概念含定义/动机/来源/疑问 4 字段
2. `drift-check.py` 输出：第一人称率 ≥0.2、平均句长 <55、空话 0 处（三项全过）
3. `notes/INDEX.md` 新增一行登记（文件名/领域/状态/一句话）
4. `loop-state.json` current_task/stage 更新到本篇
5. commit + push 成功（workspace root repo）

【失败降级】
- drift-check 不过 → 按前几篇先例织入第一人称/拆长句重跑，最多 3 轮
- 素材不足（RAG 域工件深度不够）→ web_search 补 HNSW/ANN 基础文献（Malkov-Yashunin 2016 等），标注来源日期
- 写作超时 → 落盘半成品 + loop-state 标 partial，下轮续写

## 正交维度（这篇 note 要覆盖的概念块）

| # | 概念 | 核心问题 |
|---|------|---------|
| 1 | embedding | 文本怎么变成向量，维数从哪来 |
| 2 | 余弦相似度 | 为什么比欧氏距离更适合语义比较 |
| 3 | top-k 检索 | RAG 的"召回"环节在做什么 |
| 4 | 暴力搜索 vs ANN | 规模大了为什么必须近似 |
| 5 | HNSW | 多层跳表式图索引的直觉与边界 |
| 6 | recall@k vs 延迟 | ANN 的两个旋钮怎么权衡 |
| 7 | 重排 rerank | 粗筛之后为什么要精排 |
| 8 | 切块 chunking | 切多大影响什么 |
| 9 | 本地方案成本模型 | sqlite-vec/chroma/lancedb 各适合什么规模 |
| 10 | 记忆系统里的位置 | agent 持续循环里检索是瓶颈还是噪声源 |

## 黑盒声明
- 具体产品的实时价格/性能数字不追精确值，给量级 + 口径声明（与前 5 篇一致）
- "哪个最好"不给唯一答案，给组合条件（负载×规模×驻留要求）下的判据