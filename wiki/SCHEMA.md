# SCHEMA.md - 知识体系定义

## 概念层级

```
范畴论 (Category Theory)
├── 函子 (Functors)
│   ├── Extended Functorial QFT
│   └── AQFT (Algebraic QFT)
├── 自然变换 (Natural Transformations)
├── 拓扑斯理论 (Topos Theory)
└── Cobordism
    ├── Lorentzian Cobordism
    └── Extended Cobordism

引力波天文学 (Gravitational Wave Astronomy)
├── PTA (Pulsar Timing Arrays)
│   ├── NANOGrav
│   ├── EPTA
│   └── IPTA
├── 引力波背景 (SGWB)
└── 传播理论

贝叶斯推断 (Bayesian Inference)
├── 谱指数约束
├── 最优统计量
└── 模型比较
```

## 实体类型

| 类型 | 示例 | 存储位置 |
|------|------|----------|
| 论文 | arXiv:0806.1079 | `raw/papers/` |
| 概念 | Extended Functorial QFT | `concepts/` |
| 人 | Schreiber, Brunetti | `entities/people/` |
| 机构 | NANOGrav, SKAO | `entities/orgs/` |

## 关系类型

- `references`: A 引用 B
- `extends`: A 扩展 B  
- `contradicts`: A 与 B 矛盾
- `applies`: A 应用于 B

## 向量检索配置

### 嵌入策略

1. **本地模式**：用 `sentence-transformers` 生成 embedding，存储为 JSON
2. **外部模式**：将文本导出为 Markdown，供任意向量数据库导入

### 迁移格式

```json
{
  "id": "concept-extended-fqft",
  "path": "concepts/extended_functorial_qft.md",
  "text": "...全文内容...",
  "embedding_ref": "embeddings/vectors/concept-extended-fqft.npy",
  "tags": ["category-theory", "QFT", "functorial"]
}
```
