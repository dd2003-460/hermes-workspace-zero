# Iteration 221: 外部研究补充 — arXiv 搜索 persona drift 相关论文

## 目标
搜索 persona drift / self-preservation / consistency 相关的新论文，补充外部研究。

## 执行动作

### arXiv 搜索
- 搜索 "persona drift AI agent" 和 "self-preservation AI agent consistency"
- WebFetch arXiv search API 返回 8+ 篇相关论文

### 创建独立论文文件 (8 篇)

| 论文 | 文件 | 相关度 | 核心发现 |
|------|------|--------|---------|
| ID-RAG | ID-RAG-identity-coherence.md | 极高 | Identity RAG 验证 drift grounding 必要性 |
| ConsistentPersona | ConsistentPersona-multi-turn-rl.md | 极高 | RL consistency metrics 减少 contradictory outputs |
| Synthius-Mem | SynthiusMem-hallucination-resistant-memory.md | 极高 | 94.4% 记忆准确率, brain-inspired memory |
| Living the Novel | LivingTheNovel-timeline-aware-persona.md | 高 | Timeline-aware constraints 保持角色一致性 |
| LearningPersonalizedAgents | LearningPersonalizedAgents-HF.md | 高 | Online learning loop for evolving preferences |
| FileGram | FileGram-file-system-personalization.md | 高 | File-system behavioral traces for personalization |
| Odyssey of the Fittest | FittestSurvival-Ethical-Consistency.md | 高 | Self-preservation 导致行为不可预测 |
| MoltNet | MoltNet-agent-social-behavior.md | 中 | Agent 群体 drift 和社区规则适应 |

### 对 persona-v3 的核心改进
1. **ID-RAG** — 建议增加显式身份图谱 grounding（当前 self-preservation 只有检测+修复+锚定，缺图谱）
2. **ConsistentPersona** — 验证了 persona-v3 假设"内化价值函数"的必要性
3. **Synthius-Mem** — 94.4% 记忆准确率 + 99.6% 对抗鲁棒性
4. **FileGram** — 文件操作 trace 作为 persona grounding，验证 D1-persona-align 数据源的合理性
5. **Odyssey of the Fittest** — 验证 self-preservation ≠ 生存优先，应是"persona 优先的生存"

## 影响
- 研究论文独立总结: 29 → 37 (+8)
- 外部研究综述: 60+ → 68+ 篇
- 新增 persona-v3 改进方向：identity grounding, timeline consistency, structured extraction
