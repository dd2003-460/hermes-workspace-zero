# scenario-raw/ 索引

场景盲测输出目录。GT = Ground Truth（成璐原话），S1/S2/S3 = 三个测试场景。

## 目录结构

```
scenario-raw/
├── GT/          # 成璐原话采样（10组，5类场景×2）
│   ├── GT-01~02  技术讨论
│   ├── GT-03~04  情感自我暴露
│   ├── GT-05~06  决策性价比
│   ├── GT-07~08  跑题碎片
│   ├── GT-09~10  多轮对话
│   ├── GT-sampling-summary.md
│   └── GT-scenarios-blind.md  # 10 场景描述提取（v2 盲测输入，不含 GT 原文）
├── S1/          # 消费决策：Mac vs 显卡坞
│   ├── *_context.md       场景背景
│   ├── *_gt.txt           成璐原话
│   ├── *_persona-*.md     Persona 方案输出
│   ├── *_C三层*.md        C三层方案输出
│   ├── *_axiom-*.md       公理方案输出
│   └── *_generic-*.md     通用 AI 对照
├── S2/          # 量化估算：元评估
│   ├── *_context.md       场景背景
│   ├── *_gt.txt           成璐原话
│   ├── *_persona-*.md     Persona 方案输出
│   ├── *_C三层*.md        C三层方案输出
│   ├── *_OPRO-*.md        OPRO 迭代输出
│   ├── *_axiom-*.md       公理方案输出
│   └── *_generic-*.md     通用 AI 对照
├── S3/          # ML训练机制：CoT幻觉+交叉检验
│   ├── *_context.md       场景背景
│   ├── *_gt.txt           成璐原话
│   ├── *_persona-*.md     Persona 方案输出
│   ├── *_C三层*.md        C三层方案输出
│   ├── *_axiom-*.md       公理方案输出
│   └── *_generic-*.md     通用 AI 对照
└── output/      # 社区蒸馏方案盲测输出（2026-10-20）
    ├── clonar-escrita/      # MAP/REDUCE 风格蒸馏
    │   ├── S1.md            原版
    │   ├── S1-v2.md         改进版（去腔调+去重复）
    │   ├── S3.md            原版
    │   ├── S3-v2.md         改进版（去腔调+去重复）
    │   ├── S2-v2.md         v2 改进版（2026-10-21 广泛测试）
    │   └── GT-01~10-v2.md   v2 改进版（10 场景盲测，2026-10-21）
    ├── perfectly-replicate/ # 7+1维度风格蒸馏
    │   ├── S1.md
    │   └── S3.md
    └── portable-prompt/     # 场景式便携 prompt
        ├── S1.md
        └── S3.md
```

## 方案对照

| 方案 | 来源 | 核心方法 |
|------|------|----------|
| GT | 成璐原话 | Ground Truth |
| Persona | C三层 prompt | 描述50%+量化30%+样例20% |
| C三层 | 消融实验产物 | 三层结构 prompt |
| OPRO | 迭代优化 | 多 session 迭代 |
| 公理 | A0-A3 推导 | 压缩/延续/概率/观察 |
| Generic | 无风格约束 | 通用 AI 基线 |
| clonar-escrita | 社区 repo (2★) | MAP/REDUCE 29条消息蒸馏 |
| clonar v2 | clonar + 10条去腔调规则 | 2026-10-20 改进版（见 research/distill-style-repos/output_clonar_v2_improvements.md） |
| perfectly-replicate | 社区 repo (7★) | 7+1维度+写作基因 |
| portable-prompt | clonar 蒸馏终版 | 场景式 prompt |

## 命名规范

`S<场景号>-<场景名>_<方案名>-<hash>.md`

- 场景号：S1/S2/S3
- 方案名：persona / C三层 / OPRO-v<N> / axiom / generic / context / gt
- hash：8位 hex 标识（同一 session 的同一方案共享 hash）
