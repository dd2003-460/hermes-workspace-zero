origin: ai
输入路径: tasks/02-information-research-r3.md(一手✓) + tasks/02.5-cross-check-r3.md(交叉✓) + tasks/04.5-final-review-r2.md(反方O1-O12处置)
观察时间: 2026-09-25T16:45+08:00 (Asia/Shanghai)

# 阶段 03 r3 工件：行动 DAG 重建（反方修正采纳, 回03 repair）

## 触发
04.5-r2 Reviewer=revise→回02→02.5(一手✓)→回03: 反方O6/O7/O8/O9/O10/O12 需重建排序/形态/可服务尺寸/分类/删除性价比/定义candidate universe。

## 反方修正采纳清单（→DAG节点）
| 反方ID | 修正 | 本DAG节点 |
|---|---|---|
| O6 | 显排序两维度(容量/带宽分开)+B300/MI325X/MI355X插入 | N4a(容量)+N4b(带宽) |
| O7 | GB200/GB300=rack-scale非单卡, 剥离 | N5(形态分层, rack独立) |
| O8 | 显存≠可服务尺寸, 新增维度 | N6(可服务尺寸, 需量化/KV/context/concurrency/TP-PP/engine) |
| O9 | Groq/Cerebras=专用非VRAM横比, 分类修正 | N7(专用平台分类) |
| O10 | 性价比排序证据不足→删除 | (删除, 无节点) |
| O12 | 先定义candidate universe | N0(范围定义前置) |

## N0 candidate universe 定义（O12, 前置）
- 通用单卡/8-GPU节点: H100/H200/B200/B300(单GPU口径) | MI300X/MI325X/MI350X/MI355X(+MI350P)。
- 机柜级平台(整机项目, 非单卡横比): GB200 NVL72 / GB300 NVL72。
- 专用推理系统/托管API(非VRAM横比): Groq LPU/GroqCloud, Cerebras CS-4/WSE-3/Cerebras Inference。
- 横比维度仅适用: 通用单卡/节点层。

## 行动 DAG（节点+依赖+产出+验收）
```
N0(定义universe) ─┬─ N1(一手规格表, 已✓02r3)
                  ├─ N4a(容量排序, 仅通用单卡)
                  ├─ N4b(带宽排序, 仅通用单卡)
                  ├─ N5(形态分层: 单卡|8GPU|NVL72 rack|专用)
                  ├─ N6(可服务尺寸维度: 显存→可服务需量化/KV/context/concurrency/TP-PP/engine)
                  └─ N7(专用平台分类: Groq/Cerebras 非VRAM横比)
N1 ──→ N4a/N4b/N5/N6/N7(依赖一手规格)
N4a+N4b ──→ N8(两维度结论, 不合并)
N5+N7 ──→ N9(形态/分类分层结论)
N6 ──→ N10(可服务尺寸边界: 需用户场景+engine实测)
```

## 节点产出（一手✓口径）
- N4a 容量排序(通用单卡HBM): MI350X/MI355X(288)≈B300(288,GB300推算) > MI325X(256,边界) > MI300X(192) > B200(180) > H200(141) > H100(80)。
- N4b 带宽排序(通用单卡): MI350X/MI355X/B300(8)≈B200(8,官方口径) > MI300X(5.3) > H200(4.8) > H100(3.35)。
- N5 形态: 单卡(H100/H200/B200/B300/MI*) | 8-GPU节点(HGX/AMD) | NVL72 rack(GB200/GB300, 整机) | 专用(Groq/Cerebras)。
- N6 可服务尺寸: 显存容量是上界, 实际可服务=显存−(权重+KV cache+激活+overhead), 需量化/KV策略/context/concurrency/TP-PP/engine → 边界(需实测+用户场景)。
- N7 专用平台: Groq LPU/Cerebras WSE 非通用GPU, 不能按VRAM横比; 模型覆盖=目录指定 → 分类独立。

## 删除（O10）
- 性价比排序(H200中/B200高/MI350X高): 删除, 无统一价格+同workload benchmark。

## 验收标准（04执行）
- N4a/N4b: 仅通用单卡层, 两维度不合并, 一手✓数值。
- N5: GB200/GB300 标注 rack-scale(整机), 非单卡横比。
- N6: 显存≠可服务, 边界留不补造。
- N7: Groq/Cerebras 分类独立, 非VRAM横比。
- 性价比: 已删除。

## 边界（属后续/用户）
- B300单GPU显精确(288 vs 262.5冲突, 需NVIDIA B300 datasheet)。
- MI325X精确(AMD页bot-blocked, 仅LLM口径)。
- vLLM per-GPU生产就绪(安装页不枚举)。
- 可服务尺寸(需用户场景+engine实测)。
- 价格/库存/近7天吞吐(属边界B5/B3/B7)。

## Reviewer 判定
`review: 03-r3 | action-decomposition | pass | DAG重建采纳反方O6(两维度)/O7(rack剥离)/O8(可服务尺寸)/O9(专用分类)/O10(删除性价比)/O12(universe定义前置); 节点N0-N10+依赖+一手✓口径+验收标准; 边界(B300显冲突/MI325X/vLLM per-GPU/可服务尺寸/价格)留不补造 | 修复阶段: 无(本维度通过)`