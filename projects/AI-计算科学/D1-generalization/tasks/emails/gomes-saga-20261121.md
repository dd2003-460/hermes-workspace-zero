# 草稿 · Carla P. Gomes (Cornell) · v5 2026-11-22（v4 + 背书请求附块：arXiv cs.AI 一次性背书，非 peer review，30 秒动作）
# origin: ai · 状态：待 D 确认，未发送
# 全文精读事实：主模型 Llama-3.3-70B-Instruct (80 layers)，replication 用 Qwen-2.5-14B + Gemma-2-9B（App F）；
# 方法=三独立方法交叉验证 4 阶段边界（residual cosine / linear probes / activation patching）+ attention heads 双向因果（amplify/ablate）
# 定位：她的 NoOp fragility=计算脆弱（模型属性，因果验证）；我的 A/B=信息获取脆弱（工具可修）。两者正交——
# 接缝问题：4 阶段框架是否需要一个"信息获取"前阶段？

Subject: A fourth axis for fragility: information access vs. computation?

Dear Prof. Gomes,

I'm D, a physics-background researcher working on local LLM research agents (27B-class, prompt+hook only). I read your four-stage decomposition of word-problem solving (2609.17804) in full — the three-method convergence on stage boundaries (residual dynamics, probes, activation patching) and the bidirectional causal validation of the Operation Planning heads are exactly the standard I try to hold my own experiments to.

Your NoOp fragility is a computation-stage property, causally pinned to specific heads. I ran a different kind of fragility experiment: a 27B model given only search snippets inferred a specific benchmark number from a truncated result — right by luck, unverifiable. Given a tool to read the full page, the same model refused to cite numbers it couldn't verify and separated estimates from measurements. Same weights, same task; only the tool changed. This reads as an information-access fragility, orthogonal to your four computation stages.

Two questions: (1) Does your framework need a stage-0 — information acquisition — whose fragility is tool-fixable rather than head-localizable? (2) Your replications span Llama-3.3-70B, Qwen-2.5-14B, and Gemma-2-9B; do the stage boundaries shift at the 9B scale, or is the four-stage structure scale-invariant?

A 15-minute chat or a one-line answer would both be very helpful.

One small administrative ask, separate from the above: I'm preparing to submit a paper on mechanical verification for LLM-agent reliability to arXiv (cs.AI) and ICLR 2027. arXiv requires a one-time endorsement from an established author in the category — it is not peer review, takes about 30 seconds (a 6-character code on a form), and does not require reading the paper. If you're willing, I'm happy to send the endorsement link and a copy of the paper. If not, no obligation at all.

Best regards,
D
[UCAS email]

---
字数：~200。
定位：不挑战她的结论（NoOp fragility 是模型属性，因果验证过硬），而是提出正交维度——信息获取脆弱 vs 计算脆弱。这是她框架没覆盖的轴。
P2 具体到三方法交叉验证 + 双向因果（amplify/ablate）——证明读透全文。
Q1=框架扩展问题（stage-0 信息获取），Q2=scale 问题（她做了 70B/14B/9B replication，9B 边界是否位移——她 App F 有数据，low-cost 可答）。
v4 变更：从"你的定位在能读全文时还成立吗"（挑战式）改为"正交维度+框架扩展"（建设式）——挑战式容易被"我们实验条件不同"挡掉，建设式给她一个可以接的扩展方向。
