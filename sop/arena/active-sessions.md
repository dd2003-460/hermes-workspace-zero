# Arena 活跃会话表（派发前唯一必查表）

> 一仓一会话硬约束（r80 + D 2026-11-01）：派发前查本表复用既有会话；仅当该仓库确无同向活跃会话才新开，开完立即登记本表 + `sessions.json`。同仓两个 active = 违规。
> 历史详情（事故/产出/commit）不写这里，写 `session-history.md`。本表每行 ≤2 行。

| 仓库 | 会话 | taskSpace | 当前任务 | 状态 |
|------|------|-----------|---------|------|
| prompt-first-bench | `01a1ca66-5358-7039-bcfa-b2fbf65a5a27` | tpr15-dispatch | T-PR-15/16/17 已交付(11-22) → **T-PUB-1 公式judge论文10题 已交付+核验(11-23, b148b12ed, 指纹一致, 47检查点SymPy自检PASS)**：7 full+3 rank-deficient；Lead 核 gold 发现 Q01 gold 漏 ×16 batch 因子(27b答788.5对)，已修；bool判分库已补(阻塞项#4解除) | ✅ done (11-23) |
| prompt-first-bench | `01a209ba-de48-7bc3-bf0d-b643dffb591e` | xref-q2-dispatch | **XREF-Q2 frontier 外部参照 ✅ 已交付+核验 (11-24)**：分支 `arena/dffb591e-prompt-first-bench`（= session 尾段，非 01a209ba 前缀，之前 fetch 没匹配到才误判"未跑"）；commit 51f804834，diff 仅 result.md +167；任务书 sha256 2fec587c… 独立复算一致；19 次真搜索 15m36s；核心结论：DeepSeek-Coder-V2-33B 不存在（V2 仅 16B/236B）、补全为主→Qwen2.5-Coder-32B 自托管最划算（唯一原生 FIM+HumanEval+ 87.2）、指令为主→GLM-4-32B-0414、Llama-70B W4 贴边陷阱、transfer 率是主导黑盒（arXiv:2608.13566 排名反转实锤）。**待办：rubric-v3 对照 S0-Q2 27b 基线判分（judge 族标注+仅相对有效）** | ✅ done (11-24) |
| hermes-workspace-zero | `01a213fa-75ca-7bb1-a453-3516acf4c5d9` | arena-t6-dispatch | **T6 复活前沿调研（understanding-d 4.1）**：Q1 记忆/人格持久化 / Q2 思维操作可执行编码 / Q3 外部锚点网络 SOTA(2024-2026)。任务书 `projects/AI-计算科学/D1-persona-align/tasks/understanding-d/T6-revival-frontier-research.md` @ bb2b2e9b(main)/c9afd64a(arena/423a71ef 分支)；指纹 d0fdaf81b4cf24d4；交付 `revival-frontier-research.md` | ✅ DONE (11-26 交付 a7043949 已推送；沙箱无凭据→Lead 下载 workspace zip 本地 git am+push；缺口: 异族核验/Q2 新覆盖/思考习惯原文缺失) |
| hermes-workspace-zero | `01a1f80e-4bfe-7566-9e03-52d0423a71ef` | arena-os1-dispatch-20261120 | **W6 T-PUB-1 claim强度评审 交付完成 @ df4e5d6d (arena/423a71ef 分支, 11-23 20:05)**; Lead 独立核验通过 (arena-claim-review-verification-20261123.md); 4/5 修复落地 @ 7b593678 (Q04 gold / guess_bound tol=0 / 措辞降级 / 统计修正); 剩扩题+异家族judge (workshop投后) | ✅ done-W6 (11-23) |
| prompt-first-bench | `01a20a1b-ee9f-71d4-a001-e285e40c487c` | xref-q1-arena-dispatch | **XREF-Q1 frontier 外部参照（Q1 GPU 原题 × 深 gold 37 节点/31 claim）**：✅ 已交付+核验 (11-24, 754abb8bc, +73 行, 指纹一致, 5 锚点 8/8 全中)；⚠️ gold 错配（任务书指到 3090 成本树非 Q1 原题），N-3.1 观察项不适用 → frontier 深 gold 角仍空，需换同题重派 | ✅ done (11-24) |

## 派发前检查（3 步，防连错仓库最小检查集）

1. `scripts/arena/dispatch-check.sh <repo>` —— 输出该仓活跃会话 + 门禁清单
2. 任务书已 commit+push 到目标仓库分支（`git log -1` 验证 sha）
3. prompt 显式声明目标仓库名 + 任务书路径 + 验收标准（防 agent 跨仓混用）

## 新开会话 SOP（2026-11-06 教训固化）

composer 先点 repo chip 选仓库 → 点 branch chip 选分支 → **再**发消息。直接发 clone 指令会被平台默认绑定（曾误绑 d1-video-recreation 拒执）。开完立即登记本表 + sessions.json。

### XREF-Q1（frontier 外部参照，Q1 H100 吞吐题）— DONE 2026-11-24
- session `01a20a1b-ee9f-71d4-a001-e285e40c487c`，分支 `arena/e40c487c-prompt-first-bench` @ `754abb8bc`（Create PR 后 push，1m43s，+73 行）
- 回执核验：git fetch→cat-file→diff 仅 result.md +73→任务书指纹 55ab1492… 复算一致 ✅
- 判分：Q1 自身 5 锚点 **8/8 全中**（14x误读=互联带宽比 / decode 1.68x / prefill 1.31x / NVLink 仅多卡TP / 4 缺口全列）。质量高：条件化结论 + 9 项黑盒表 + 检测出 io.net 自相矛盾（PCIe 带宽写 3.35 与 NVIDIA 规格冲突，已排除）。
- **⚠️ gold 错配（Lead 侧任务书写错）**：任务书把 Q1 指到 37 节点深 gold 树，但那棵树根节点是「3090×4 每通过任务成本」，是**另一道题**（3090 成本分解），不是 Q1（H100 PCIe vs SXM 吞吐）。Q1 的真实 gold = `experiments/stage-ablation/questions/Q1-gpu-h100.md` 的 5 锚点。N-3.1 微架构家族观察项（27b 全 0 命中）不适用 Q1。→ frontier 深 gold 角仍空，需换一道与 37 节点树同题的题重派。

### BIGDIR-review（大方向审查：Pareto 框架是否成立）— ✅ DONE 2026-11-24
- session `01a20aec-f59e-7ff8-aaee-e001da2c606b`，分支 `arena/da2c606b-prompt-first-bench` @ `153209f21`（Create PR 后 push，14m12s，+35 行）
- 任务书 `tasks/BIGDIR-review/TASK.md` @ `1fbd086c6`（tmp-lit-snowball），sha256 `78bf4221…`；19 次检索 + 5 次 fetch
- **结论（已 git show result.md 读到）**：①Pareto 不成立 conf 0.80——单轴饱和曲线被误标，领域自己撤回（arXiv:2505.20522 v1 "Test-Time Scaling **Pareto**" → v2 "**Plateau**"）②"预算必须 harness 强制"半边成立 conf 0.86（5835 runs 安慰剂对照：强制上限 > 告知预算 placebo）③最难一击 conf 0.85：matched budget 名不副实（SM 203-312 节点 vs bare 50.4，计算比 4-6×）+ 度量自指（same-family judge + depth↔长度 r=0.648=verbosity 非深度）
- **最小修法（5 条）**：改名 Pareto→"budgeted coverage scaling + harness-enforced stopping"；预算轴改 realized token；加 token-matched sham 对照臂；跨家族 judge + 长度残差化；AGI→METR horizon 表述
- 待办：goal 框架按此降级（D 已认可 Pareto 弱，等 D 确认改 goal 措辞）

### IDEA-review（7 个空白 idea 外部撞车核验+可发表性排序）— ✅ DONE 2026-11-24
- session `01a20b11-d552-79cc-be74-8222f8477718`，分支 `arena/f8477718-prompt-first-bench` @ `70dca8efa`（5 idea @ e271a44c4 + 追加 #53/#52 @ 70dca8efa）
- 任务书 `tasks/IDEA-review/TASK.md` @ `799264136`（tmp-lit-snowball），sha256 `c1aaa377…`
- **追加2（#53 信息论精化框架第三轮核验）@ 81be67cb9 (11-24)**：conf 0.7, workshop/短文级, 独立顶会难；链式域已撞（2601.23163 NeurIPS'26 E&D / 2508.03346 Step Entropy / 2604.06695 depth-wise）；最难一击=信息转发平凡性；最佳定位=并入 #10 主线离线分析章节。与内部节点级 MI 实测（5fa9dfe8b, 浅层主导+深层点增益负）交叉印证 → #53 独立 claim 不成立，收进 #10 当瓶颈定位模块
- **追加3（#53 枚举vs判断精化第四轮核验）@ 82a67df96 (11-24)**：claim 重释=深层对微架构级判断（具体哪一环）的增量贡献>浅层枚举；conf 0.6 条件可发表，make-or-break=交叉梯度实验（浅层主导 I(L;V_coarse) + 深层主导 I(L;V_fine|V_coarse)，fine-conditional 不升则 claim 死）；撞车三线占位（DDx 三阶段 2602.03340 / 信息增益消歧 2402.03271+2605.05386 / 步类型分类学 2512.14332+2512.00729），未见=树×类型×深度×信息贡献测量+两级判定交叉梯度；最难一击=同义反复+HARKing+概念已占位，守法=判据去深度化+层内类型对照+预注册 held-out+三控制臂；方法学升级 SLIDER 式 PID（2610.00571）。#53 定位不变=#10 离线分析模块，模块内容=交叉梯度测量
- **追加4（#53 投稿策略第五轮）@ 7dae6431a (11-24)**：5 对标实核（2601.23163 NeurIPS'26 E&D 已录/2508.03346 ICLR'26 正刊已录/SLIDER ICLR'26 workshop/Thought Anchors 在审/UoT NeurIPS'24）；venue 主推双轨=NeurIPS'27 E&D（P 0.30 全守法/0.15 半守法，~2027-05 截稿，分析型免 code）+ ICML'27 workshop（P 0.55/0.35）；ICML'27 main 窗口留给 #10；最快路径 3-4 周到 arXiv 可投稿态；概率=主观估计非事实
- **新任务（#10 分解树 1-loop 01）派发 11-24 13:50**：任务书 `tasks/10-decomposition/TASK.md` @ 281a1322d（arena 分支）；**✅ 完成 @ b8f7a3691**：分解树 v2 = S1-S7 正交子项 + 量化正交性核对 + 缺口标注 + 任务表（机器可查验收+耗时）+ #53 负结果模块嵌入；待 Lead 核验正交性后进入 02 信息调研
- **#53 升格独立 goal (11-24 D 指令)**：stage-gate `idea53-cross-gradient`（6 阶段，全平台共享含 qqbot）；goal 三件套 `pfb/tasks/idea53-goal/`（GOAL.md 含 §0 完整逻辑链+§7 arena 看法+§8 qqbot 接手入口 @ 0d0fffd79 / decomposition.md T1-T7 @ 40f5cef09 / 预注册锚点 20c029300）；T1-T3 subagent deleg_53e3a082 running
- 触发：D「其余 idea 你也问一遍」
- 7 个 idea：#10 正交完备分解 / #30 prompt-only 消融 / #31 公式vs文字 / #32 压缩即智能MDL / #40 压缩阶梯K复杂度 / #53 树级深节点信息增益 / #52 发现-行动断裂
- **结论（git show result.md 读到）**：总排序 #10→#32→#53→#52→#30→#31→#40；**#10 top-1**（唯一可量化终点+ADaPT/VeriMAP 头对头+组合窄空白）；#31 直接撞车 UtilityMax(2603.11583) 降级 replication；#40 建议砍（K 不可计算）；#53 强近邻 IGRPO/Thought Anchors/2411.11984，剩空白=深度梯度实证+瓶颈定位应用 conf0.45，建议作主线瓶颈定位模块；#52 直接近邻 Knowing but Not Showing(2605.25284) conf0.6。一个主线论文吃下全部 7 个 idea。
- 注：追加轮 prompt 发送时 shell 变量展开失败（发出 `${PROMPT}` 字面量），agent 从会话历史推断任务完成，核验方向与精化框架一致，结果可用。
