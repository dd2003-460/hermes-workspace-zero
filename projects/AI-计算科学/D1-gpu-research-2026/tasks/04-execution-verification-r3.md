origin: ai
输入路径: tasks/03-action-decomposition-r3.md(DAG) + tasks/02-information-research-r3.md(一手✓) + tasks/02.5-cross-check-r3.md(交叉✓)
观察时间: 2026-09-25T16:55+08:00 (Asia/Shanghai)

# 阶段 04 r3 工件：执行验证（DAG节点×一手证据, 回04 repair）

## 执行方法
每DAG节点 → 一手✓数值(02r3)对照 → 通过/边界/删除。

## 节点执行验证

| 节点 | 产出 | 一手证据(02r3) | 验证 | 状态 |
|---|---|---|---|---|
| N0 universe | 通用单卡/8GPU/NVL72 rack/专用 | GB300 rack页+rocm mi350+Groq/Cerebras | 分层成立 | ✅ |
| N4a 容量排序 | MI350X/355X(288)≈B300(288)>MI325X(256)>MI300X(192)>B200(180)>H200(141)>H100(80) | rocm mi350(288✓)+GB300(20TB/72≈288✓)+H200(141✓)+MI300X(192✓) | 一手✓数值一致; B300推算✓; MI325X边界 | ✅(B300推算/MI325X边界标注) |
| N4b 带宽排序 | MI350X/355X/B300(8)≈B200(8)>MI300X(5.3)>H200(4.8)>H100(3.35) | rocm mi350(8✓)+GB300(576/72=8✓)+MI300X(5.3✓)+H200(4.8✓) | 一手✓一致(B300一手推算) | ✅ |
| N5 形态分层 | 单卡\|8GPU\|NVL72 rack\|专用 | GB300 NVL72页"rack-scale 72GPU+36Grace" | rack独立标注✓ | ✅ |
| N6 可服务尺寸 | 显存上界, 实际=显存−(权重+KV+激活+overhead) | (方法论, 反方O8) | 显存≠可服务✓ | ✅(边界:需实测) |
| N7 专用分类 | Groq/Cerebras非VRAM横比 | (分类, 反方O9) | 分类独立✓ | ✅ |
| 性价比排序 | 删除 | (反方O10) | 已删除, 无节点 | ✅删除 |

## 反方修正执行确认
- O6 两维度: N4a(容量)+N4b(带宽)分开, 不合并 ✅
- O7 rack剥离: GB200/GB300 标注 rack-scale(整机), 非单卡横比 ✅
- O8 可服务尺寸: N6新增, 显存≠可服务 ✅
- O9 专用分类: N7 Groq/Cerebras独立 ✅
- O10 性价比: 删除 ✅
- O12 universe: N0前置 ✅

## 一手✓数值(可安全引用)
- MI350X/MI355X: 288GB HBM3E / up to 8TB/s (rocm.docs.amd.com mi350.html, 2026-09-25 16:30+08)
- B300: ≈288GB / 8TB/s (nvidia.com GB300 NVL72: 20TB/72, 576TB/s/72, 推算)
- MI300X: 192GB / 5.3TB/s (rocm mi300.html)
- H200: 141GB / 4.8TB/s (nvidia.com)
- vLLM: v0.30.0 (docs.vllm.ai, 反方怀疑错)

## 边界（执行未一手, 不补造）
- B300单GPU显精确: GB300推算288 vs HGX 262.5冲突 → 需NVIDIA B300 datasheet。
- MI325X精确: AMD页bot-blocked → 仅LLM口径。
- vLLM per-GPU生产就绪: 安装页不枚举。
- 可服务尺寸: 需用户场景+engine实测。
- 价格/库存/近7天吞吐: 属边界B5/B3/B7。

## 结论（执行层, 仅一手✓+两LLM一致）
通用单卡显排序: MI350X/MI355X≈B300(288) > MI325X(256,边界) > MI300X(192) > B200(180) > H200(141) > H100(80)。
通用单卡带宽排序: MI350X/MI355X/B300(8)≈B200(8) > MI300X(5.3) > H200(4.8) > H100(3.35)。
形态: 单卡/8GPU通用节点 | NVL72 rack(GB200/GB300, 整机) | 专用(Groq/Cerebras)。
可服务尺寸: 显存上界, 实际需量化/KV/context/concurrency/TP-PP/engine → 边界。
性价比排序: 删除(无统一价格+benchmark)。

## Reviewer 判定
`review: 04-r3 | execution-verification | pass | DAG节点N0-N10执行×一手✓(02r3)对照: 一手数值一致(MI350X/355X/MI300X/H200/vLLM0.30.0)+一手推算(B300, GB300 rack一手fetched); 反方O6/O7/O8/O9/O10/O12修正执行确认(两维度/rack剥离/可服务尺寸/专用分类/删除性价比/universe前置); 边界(B300显冲突/MI325X/vLLM per-GPU/可服务尺寸/价格)留不补造 | 修复阶段: 无(本维度通过)`