# 02-information-research — 素材盘点（KB.1 第6篇）

## 本地素材（已读，可直接引用）

### decomp T17 rag-vs-longctx gold tree（projects/decomp/bench/gold-rag-vs-longctx/tree.md）
- RAG 正确率侧拆解：P(correct) = P(拿到相关ctx) × P(ctx内答对) × (1−halluc)
- ctx_recall 四因子：chunk_quality / embed_quality / rerank_gain / in_ctx_localization
- chunk 级召回是"RAG 头号失效模式"——切块破坏段落完整性
- recall@k 曲线选拐点 k 是嵌入模型选型的标准动作
- 重排判据：rerank 前后 recall@3 差值 vs 其延迟/成本
- 向量库查询成本节点（N-2.2.2）+ 检索延迟 p50/p95（嵌入+向量检索+重排）
- 候选库点名：Qdrant/Milvus/pgvector（云端口径），数据出域约束

### decomp T17 run-a/run-b（qwen3.8-27b 直跑工件）
- run-a：embedding 环节定性为"CPU/GPU 极快，忽略不计"+ HNSW/IVF 微秒级
- run-b 量化估算（可作 note 里的量级锚）：2亿 token × 1536维 × 4字节 ≈ 1.2TB 原始向量；HNSW 索引常驻内存需 ~1TB RAM 服务器
- run-a 嵌入模型对比锚：BGE-M3 vs OpenAI Ada-002，recall 差距可达 5-10%

### KB 前 5 篇的格式先例
- gpu-inference-hardware.md：8 概念块 + 可证伪预测带判死条件（本篇沿用该收尾结构）
- agent-memory-mechanisms.md：agent 记忆三组件（工作窗口/外置存储/检索）——本篇接住"检索"这一环往下钻

### memory-benchmarks LoCoMo 实验（T17-full，进行中）
- 10 对话 ~300 题的长对话记忆问答，answerer/judge=qwen3.8-27b
- 与本篇关联：LoCoMo 考的是"从长历史里找对信息再答"，正是检索+定位的端到端测试；当前在 ninfer :8787 上跑，~110s/题
- 引用口径：作为"为什么 agent 记忆需要检索"的实证锚，不引用未完成的分数

## 外部文献（写作时按需补，标注来源日期）
- Malkov & Yashunin, "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs", IEEE TPAMI 2018（arXiv 2016）——HNSW 原文
- Johnson, Goubran, et al., "Billion-scale similarity search with GPUs" (FAISS), 2019——IVF/PQ 系
- 本地方案：sqlite-vec / chroma / lancedb 的 README 规模定位（写作时 web_search 核对一次，给量级不给精确值）

## 黑盒声明
- 产品性能数字只给量级（μs 级检索、GB 级索引），不追实时 benchmark
- "哪个库最好"不给唯一答案，按负载×规模×驻留要求给判据（与前 5 篇一致）