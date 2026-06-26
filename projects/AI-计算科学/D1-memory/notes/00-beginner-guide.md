# D1-memory — 记忆系统与用户配置 — 初学者指南

> **项目**: D1-memory
> **状态**: ✅ 归档完成（探索记录已全部分发到各项目）
> **创建**: 2026-05-17, **最后更新**: 2026-05-24

---

## 一、工作起点

**核心问题**：在多 agent、多 session 的工作环境中，如何管理探索记录、用户画像和系统配置，使得信息不丢失、可检索、可分发？

## 二、前人调研

- AGENTS.md 红线 0 原则：探索记录保存在 memory/，不可删除
- Hermes agent 的记忆机制（~/.hermes/memory/）
- OpenClaw workspace 的 memory/ 结构

## 三、相似工作

| 工作 | 相似度 | 不同 |
|------|--------|------|
| Obsidian vault | 40% | 通用笔记，我们针对 agent 工作流 |
| Logseq | 30% | 日记导向，我们是项目导向 |

## 四、工作逻辑

```
Step 1: 建立 memory/ 分层结构（exploration/processed/profile/raw/checkpoint）
Step 2: 探索记录按领域分发（理论物理→D1-grav-waves，认知→D1-academic-AI）
Step 3: 索引化（每个子目录有 INDEX.md）
Step 4: 归档完成，D1-memory 自身只剩框架文件
```

## 五、填补空白

- 建立了多 agent 工作区的记忆分层管理标准
- 定义了"探索记录不可删除，只移动归档"的纪律

## 六、对标贡献

| 维度 | 对标 |
|------|------|
| 类型 | 基础设施 / 工程实践 |
| 价值 | 为整个 workspace 提供记忆管理框架 |

---

*origin: ai*
