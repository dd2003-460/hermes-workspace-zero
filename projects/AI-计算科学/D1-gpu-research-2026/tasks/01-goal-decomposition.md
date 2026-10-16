origin: ai
输入路径: /Users/a1-6/Desktop/workspace/projects/D1-gpu-research-2026/ (任务输入: 调研 GPU 推理硬件选型)
观察时间: 2026-09-25T01:30+08:00 (Asia/Shanghai)

# 阶段 01 工件：目标、因素与空缺条件

## 1. 决策问题与交付物

- **要决定什么**：在 2026-09 当前市场条件下，哪些 GPU 硬件平台适合 LLM 推理（inference）部署，以及选型依据。
- **为谁**：成璐 / 项目 D1-gpu-research-2026 决策者（推理硬件采购或租用决策）。
- **成功可验证定义**：交付一份选型结论，每个关键数值（型号、显存、价格、吞吐、支持状态）有 ≥2 独立可追溯来源，近 7 天证据优先；时间敏感未证实项标"未解决"；适用边界与残余缺口坦诚列出。
- **范围**：数据中心/工作站级 GPU 推理（NVIDIA 为主，含 AMD/国产加速器候选），覆盖规格、价格、推理吞吐、软件支持、近 7 天证据。
- **不做什么**：训练集群选型、CPU 推理、边缘 MCU、具体云实例定价谈判、最终采购执行。

## 2. 已知条件表

| 项 | 类型 | 来源路径 |
|---|---|---|
| 项目目录存在含 notes/memory/tasks | project-derived | /Users/a1-6/Desktop/workspace/projects/D1-gpu-research-2026/ |
| 阶段规格 01→04.5 共 6 文件 | project-derived | /Users/a1-6/Desktop/workspace/loop/1-loop/main-8.7-loop/ |
| ego-browser CLI 可用 (/Users/a1-6/.local/bin/ego-browser) | project-derived | 本会话 Bash 观察 2026-09-25 |
| 调研主题=GPU 推理硬件选型 | human-provided | 任务输入（启动 prompt） |
| 默认决策画像=推理部署性价比 | assumed default | 任务输入未给预算/场景，可逆假设 |

## 3. 正交因素表

| ID | 定义 | 边界 | 优先级 | 对结论影响 | 与相邻因素区别 |
|---|---|---|---|---|---|
| F1 | 显存容量 (VRAM GB) | 单卡显存 GB；决定最大可加载模型/批 | 高 | 决定能否跑大模型 | 区别于 F2 带宽（容量 vs 速率） |
| F2 | 显存带宽 (GB/s) | HBM 带宽；决定 token 生成速率上限 | 高 | 决定 decode 吞吐 | 区别于 F3 算力（带宽 vs FLOPS） |
| F3 | 推理算力/吞吐 (tokens/s, FLOPS) | 实测或官方 tokens/s 或 TFLOPS | 高 | 决定 prefill/吞吐 | 区别于 F2（带宽）与 F4（成本） |
| F4 | 价格/成本 (USD, 单卡/租赁) | 当前报价或官方 MSRP | 高 | 决定性价比 | 区别于 F6 功耗（购置 vs 运行成本） |
| F5 | 软件生态与支持状态 | CUDA/框架(vLLM/TensorRT/SGLang)支持版本 | 高 | 决定可部署 | 区别于 F7 可用性（软件 vs 硬件获取） |
| F6 | 功耗与能效 (W, perf/W) | TDP 与 perf/W | 中 | 决定运行成本/散热 | 区别于 F4（运行 vs 购置） |
| F7 | 部署形态与可用性 | 单卡/服务器/云实例、近 7 天可获取 | 中 | 决定实际可采购 | 区别于 F5（获取 vs 软件） |
| F8 | 互联/多卡扩展 | NVLink/带宽、多卡并行 | 中 | 决定多卡可行 | 区别于 F2（片间 vs 片内带宽） |
| F9 | 候选 GPU 选型空间 | 哪些 GPU 平台进入选型候选集合（NVIDIA H100/H200/B200/GB200, AMD MI300X/MI325X, 国产 Ascend 910B/910C, 专用 ASIC Groq/Cerebras 等）；决定 F3/F4 性价比比较的边界 | 高 | 决定性价比排名范围 | 区别于 F1-F8（属性 vs 候选集合） |

## 4. 空缺清单

| 空缺 ID | 因素 | 可核验具体问题 | 为何未证实 | 阻塞判断 | 阶段02首选来源/搜索词 | 备用 |
|---|---|---|---|---|---|---|
| G1 | F1 | 当前主流推理 GPU 显容量（H100/H200/B200/MI300X/MI325X 等 GB） | 无当前来源 | 能否加载大模型 | "NVIDIA H200 HBM3e memory GB" 官方规格页 | TechPowerUp DB |
| G2 | F2 | 各型号显带宽 GB/s | 无当前来源 | decode 吞吐上限 | "H200 memory bandwidth TB/s" | 厂商 datasheet |
| G3 | F3 | 近 7 天独立推理吞吐 benchmark (tokens/s) | 无当前来源 | 性价比排名 | "GPU inference benchmark tokens/s 2026" | MLPerf / ArtificialAnalysis |
| G4 | F4 | 当前单卡/租赁价格 | 时间敏感 | 性价比 | "H100 price 2026" / "B200 price" | 云实例报价 |
| G5 | F5 | vLLM/TensorRT 当前支持型号与版本 | 无当前来源 | 可部署 | "vLLM supported GPUs 2026" | 官方 docs |
| G6 | F6 | 各型号 TDP 与能效 | 无当前来源 | 运行成本 | "H100 TDP watts" | 厂商 spec |
| G7 | F7 | 近 7 天可获取/库存/新发布 | 时间敏感 | 实际采购 | "GPU availability news last 7 days" | 厂商 newsroom |
| G8 | F8 | NVLink/互联带宽当前世代 | 无当前来源 | 多卡并行 | "NVLink bandwidth H200 B200" | 厂商 spec |
| G9 | F9 | 当前推理 GPU 候选集合完整枚举（各厂商各型号, 近7天可获取） | 候选集合未定义 | 性价比排名边界 | "inference GPU 2026 list NVIDIA AMD Ascend Groq Cerebras" 厂商 lineup + 独立选型指南 | 厂商 product page / MLPerf 提交列表 |

## 5. 阶段 02 研究队列（按优先级）

0. **G9 候选 GPU 集合枚举**（先定义边界）— 各厂商各型号进入候选集合，否则 F3/F4 性价比排名边界未定义。
1. G1+G2+G6 规格核验（显容量/带宽/TDP）— 官方 datasheet 一手。
2. G3 近 7 天独立吞吐 benchmark。
3. G4 当前价格（官方 MSRP + 独立报价）。
4. G5 软件支持状态（vLLM/TensorRT 版本）。
5. G7 近 7 天发布/库存新闻。
6. G8 互联带宽。
7. Ego Lite 网页 LLM ≥2 服务提交（阶段 02 硬门槛）。

## 6. 覆盖与可追溯性表

| 目标/约束 | 因素 ID | 空缺 ID | 阶段02研究问题 |
|---|---|---|---|
| 能否加载大模型 | F1 | G1 | 显容量 GB |
| decode 速率 | F2 | G2 | 显带宽 GB/s |
| 吞吐性价比 | F3,F4 | G3,G4 | tokens/s + 价格 |
| 可部署 | F5 | G5 | 框架支持版本 |
| 运行成本 | F6 | G6 | TDP/能效 |
| 可采购 | F7 | G7 | 近7天获取 |
| 多卡可行 | F8 | G8 | 互联带宽 |
| 性价比排名边界 | F9 | G9 | 候选 GPU 枚举（先定义边界再比较） |

**失败点/诚实标注**：默认决策画像"性价比"为 assumed default（可逆）；预算上限与具体模型尺寸未给，故 F3/F4 性价比权重未定—阶段02 收集事实，阶段04.5 适用边界需用户场景。无未覆盖交付物。

**round 2 正交补充（用户指出缺陷）**：r1 把 F1-F8 全部为属性，未把"候选 GPU 选型空间"作为正交因素 → F3（算力/性价比）比较边界未定义 → 阶段02 搜索空间隐式收窄到 NVIDIA 旗舰+vLLM，AMD/国产/ASIC 未搜索。本轮补 F9（候选集合）+G9（枚举）+队列步骤0（先定义边界再比较）。