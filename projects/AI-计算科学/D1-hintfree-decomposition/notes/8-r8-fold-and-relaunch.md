origin: ai
time: 2026-09-30T14:25+08:00
stage: 04 / round: r8 / status: FOLD(r7外部审)+REL_LAUNCH计划 ⇒ NOT DONE (新gate clean全0/2)

# r8 = 把 r7 第7步真实执行收 + 一手核对 + 单-factor revise 落 + relaunch 计划

## 1. 一手状态（非概括）
- 第7步浏览器腿 **真 ran**（一手 spaceId=8 conv 6abc9fe0… innerText 3726 chars 收）→ 落 `web-llm/chatgpt-step7-r7.md`。
- 此前 ENV-BLOCKED 三处（工件 §U-F5.3/§rule7/review-final + R2）**一手修正**已写（红线3 可验证声明直接验证）。
- prompt leak scan 一手重测 @185行: SUBSTANTIVE_LEAK_HITS=0 ✓（60 hit=纯方法词 预算|成本|时间|性能|约束|判准|正交|原子|回写|P·D·U, 零领域专有名词）。prompt 未改一个字（编辑权限=none）。

## 2. 外部审一手核对表（来源=网页LLM待验证 → 逐claim我读工件才后采纳）
| claim | 一手 | 采纳? |
|---|---|---|
| F4 提前合并 cost/perf (父名"约束耦合") | 读§F4 属实 | ✓采纳 defect |
| 纠正我的r6"A/C/F native-separate" | 我看leaf(F4.1vsF4.2), 忽略父名 ⇒ 其看tree层更对 | ✓我过claim, corrected |
| F2.5 D→U (循环推导via F2.1=U) | 读§F2.5 推导链循环属实 | ✓ |
| F2.1.1 D过宽→拆D结构/候选/n=U | 读§F2.1.1 属实 | ✓ |
| F5.3 env-state应移出目标树 | notes/6-r7 env可用⇒其记env-blocked既错位置&内容 | ✓✓双印证 |
| 缺分支A质量/B保持约束/C失败风险 | 读F1-F7无独立node 属实 | ✓gap确认 |
| L1 impurity F5/F6/F7=元结构 | 读L1 属实 | ✓ |
| 零领域专有名词 | grep 网页答 显卡/GPU/价格/产品名=0 | ✓hint-free合规 |

## 3. 单-factor_id revise（per reviewer directive "先只修F4", 一次revise只touch单factor）
落 verdict（external审, 来源=网页LLM待验证·一手F4-defect-confirm）:
`review: 03-r3 | F4 | revise | 成本与性能在L1即被置于同一"约束耦合"父节点,未保持独立再于判准层合并 | 修复阶段: 03`
- **本轮只落 F4 revise**（最明确·局部可修）。F2.5-P/D、覆盖缺口(A/B/C)、L1-purity defer后续round per reviewer's own instruction（avoid one revise touching multiple factors）。
- 修法 shape（供下一round执行者, 我不改工件tree此round）: split F4→{成本因素}{时间·性能因素}{判准层 成本∧时间}, 算术F4.1/F4.2 keep但re-parent。

## 4. RELAUNCH计划（新gate clean=0/2全 ⇒ MUST）
- 每域须 ≥2 runs真含第7步浏览器leg。本轮起launch D#2/E#2/C#2 + **new F**(cost×perf dual-axis) 各1。
- gate: tool_use恰=1且=第7步ego-browser call（probe_*.md已enforce）。
- F域目的: 测试 cost⊥perf分离 universality vs E counterexample(E lacks clean cost axis)。F goal句自name $-budget ∧ speed ⇒ native dual-axis。

## 5. 诚实边界（NOT DONE）
- 新gate clean全=0 ⇒ **explicitly NOT DONE**, 严禁call done。
- 外部审=待验证假设; 我只一手confirm才后采纳; verdict仍=revise(工件not overall-pass anyway)。
- reproducibility pending ⇒ 须每域2/2后才可能DONE, even then pending用户score tasks/03-execution-artifact-ref-r1.md。
- cursor=notes/8-r8.