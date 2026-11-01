# 领域 SOP：黑洞质量谱出图清单（CosmoBH-Spectrum）

> 定位：这是本仓库的**可执行标准作业程序（SOP）**——告诉任何人（包括 Arena agent）
> 接下来出什么图、用什么数据、怎么算、怎样算对。调研依据见
> `artifacts/相关工作调研_近十年BH质量谱.md`（24 篇文献全部经 arXiv API 核实）。
>
> **为什么命名是 SOP 而不是"风格/倾向/规则"**（2026-10-16 用户明确问过）：
> - **风格（style）**=审美偏好（颜色、字体）——agent 无法据此行动，且会抑制创造力；
> - **倾向（preference）**=主观偏好（"偏好对数坐标"）——不可验收；
> - **规则（rule）**=单点硬约束（"不许改单位"）——只管一条，管不了流程；
> - **SOP**=带步骤、输入、输出、判据的作业程序——**agent 能照着跑、人能照着验收**。
> 本文档因此命名为 `docs/领域SOP_出图清单.md`，与调研纪要（artifacts，证据层）分工：
> artifacts 回答"领域怎么做"，docs/SOP 回答"我们接下来怎么做"。

---

## 1. 工作重心（三条战线，按优先级）

| 战线 | 内容 | 状态 |
|---|---|---|
| **S1 目录原生质量谱** | 用 TNG 目录原值画 BHMF/SMF/标度关系/占据率（郭老师拍板路线） | 进行中（fig1/fig2 已出，见 §3 P0） |
| **S2 遗迹推前质量谱** | IMF + Spera 遗迹 + 宇宙学推前 → 恒星 BH 遗迹 MF 随红移（对标 Sicilia+2022 I） | 待出图（P0-5） |
| **S3 种子桥接** | S2 的遗迹分布当轻种子 → 半解析生长 → 与 S1 的 SMBH 段对话 | P1（概念+首版图） |

---

## 2. 通用口径约定（所有图必须遵守）

| 项 | 约定 | 理由 |
|---|---|---|
| 质量单位 | 图内一律 `Msun/h`，轴标签写明；转物理 Msun 需乘 h | 数据原生单位，不自作主张 |
| 密度单位 | `h^3 Mpc^-3`（质量函数）、`Msun/h Mpc^-3`（密度） | 与体积 75³ (Mpc/h)³ 自洽 |
| 晕质量定义 | 目录 `m_h` 原生定义（TNG-Dark FO F 口径，见 `1_Data_Ingestion_Cosmology/1.2_Simulation_Extractor/notes/TNG数据说明书.md`） | 不做未标定的定义转换 |
| 红移来源 | header 组快照表（snap=99→z=0，snap=0→z=20.05） | 与数据一致 |
| 图内文字 | **中文标题/轴标签**（默认；投稿英文期刊时再切英文）。本机 matplotlib 已配中文字体回退（rcParams sans-serif 含 STHeiti/Songti 等），教学示例 6 图已验证无方框 | caveat 仍写进 JSON 与 README，不写进图 |
| caveat | 每张图配一个 JSON 记录：数据列、单位、快照、筛选条件、caveat 文本 | 数据来源未经独立确认，必须可追溯 |
| 低质量端截断 | `m_bh`/`m_s` 非零值仅 tree.0–5 有（>3.6e9 Msun/h），低端尖峰≈3387 Msun/h 是经验绘制硬下限，**不是物理** | 取证报告结论，随图注明 |

---

## 3. 出图清单

### P0（优先出，数据现成）

#### 图 P0-1：多红移黑洞质量函数 BHMF(z)
- **物理问题**：黑洞数量随质量与红移怎么分布？高低端有没有模拟对比中发现的
  "低端不足/高端超量"问题（Habouzit+2021）？
- **数据**：目录 `m_bh`（>0）、`m_h`、`snap`→z；体积 75³ (Mpc/h)³。
- **对标**：Sijacki+2015 Fig.3、Habouzit+2021 BHMF 面板。
- **做法**：z=0/0.5/1/2/4/6 各画 Φ(logM)=dN/(dV dlogM)；bin 宽 0.25 dex；
  各红移用对应快照的共动体积（75³ 恒定，共动坐标下无需修正）。
- **判据（怎样算对）**：①数量级与 Habouzit+2021 的 TNG100 BHMF 同量级（±1 dex 内）；
  ②低质量端尖峰可被 3387 Msun/h 硬下限解释（在 caveat 里点名）；
  ③z 升高高端压低、低端相对变平——若出现高端随 z 反常抬升需复查筛选。
- **caveat**：重子字段经验绘制、仅 tree.0–5 非零。

#### 图 P0-2：黑洞占据率 f_occ(M_halo, z)
- **物理问题**：多大质量的晕里"有 BH"的比例是多少？随红移怎么变？
  （Weller+2026 把它当作播种/动力的化石记录。）
- **数据**：`m_bh`（=0 vs >0）、`m_h`、快照。
- **对标**：Weller+2026 ApJL 1008 L54；Tremmel+2023。
- **做法**：按 log m_h 分 10 档，每档算 m_bh>0 比例；z=0/1/2/4 四条曲线；
  同时给出 m_bh 阈值扫描（>1e6/>1e7 Msun/h 各一版）。
- **判据**：①f_occ 在 m_h ≳10^11.5 Msun/h 应趋近 1（该尺度以上晕必有 BH）；
  ②阈值越高曲线越靠右移；③z 越高同质量端 f_occ 越低（早期播种不足）——
  若 z 升高 f_occ 反而升，说明非零值分布与红移的相关性异常，需复查。
- **caveat**：占据率是"经验绘制的 BH 列非零比例"，不是物理播种概率。

#### 图 P0-3：标度关系演化（MBH–M⋆ / MBH–M_h / MBH–v_max）
- **物理问题**：黑洞–宿主共演化关系长什么样？随红移怎么动？
- **数据**：`m_bh`、`m_s`、`m_h`、`v_max`（v_max 单位 1e3 km/s，MW 中位 191 km/s）。
- **对标**：Habouzit+2021 Fig.1–2、Ni+2022 Fig.3–4、Xu+2020（MBH–σ）。
- **做法**：散点（淡）+ 中位数趋势（粗）+ 16–84 分位带；z=0/1/2/4 分面或叠画；
  MBH–v_max 即数据版的 M–σ（v_max 是晕速度，σ≈v_max/√2 量级，只作定性对标）。
- **判据**：①MBH–M⋆ 斜率 0.5–1.5 量级、Spearman 相关 >0.5；
  ②低质量端（M⋆<10^9.5 Msun/h）趋势变平/发散——与 Habouzit"低端无紧关系"一致；
  ③v_max 版应给出比 m_h 版更紧的关系（速度是比质量更"局域"的量）。
- **caveat**：MBH–v_max 不是标准 M–σ（σ 是恒星速度弥散），只能定性。

#### 图 P0-4：恒星 BH 遗迹质量函数随红移（4.1 推前输出）
- **物理问题**：从 Salpeter IMF + Spera 遗迹关系推前，宇宙里恒星质量黑洞的
  数量–质量分布随红移怎么变？（对标 Sicilia+2022 I 的核心图。）
- **数据/管线**：1.1 宇宙学 + 2.1 IMF + 2.2 遗迹质量 + 4.1 推前（现有
  `compute_bh_spectrum`/`quantify_pisn_effect.py` 可直接产数）。
- **对标**：Sicilia+2022 I Fig.2/4（形状：~50 M☉ 以下平、以上对数正态尾；
  本地遗迹密度 ρ•≈5×10⁷ M☉/Mpc³）。
- **做法**：z=0/0.5/1/2/4 的遗迹 MF；同时出 PISN none vs S17 的差异带
  （S15 在当前配置是恒等变换，只作注释）。
- **判据**：①MF 形状呈"平段+对数正态尾"；
  ②MW 标定（4.547182e-03/yr 量级）与现有基线一致（物理不变量逐位不变）；
  ③S17 与 none 的差在低 Z 显形（间隙 [58.6,83.0] Msun）——已量化，见
  `artifacts/pisn_experiment/`。
- **caveat**：遗迹 MF 不含双星通道修正（Sicilia 有，我们未做，标注为简化）。

#### 图 P0-5：目录原生 BHMF/SMF 汇总图（已有 fig1 的规范化版）
- 把 `artifacts/tng_catalog_figures/fig1` 升级为 SOP 格式：按 §2 口径重画，
  JSON 补齐 caveat 字段，作为 S1 的基线存档。

### P1（第二批）

#### 图 P1-1：BHMF 的"活跃/沉寂"分解
- 用 `m_s>0`（有恒星质量即判为有星系活动代理）拆 BHMF 的两段贡献，
  定性复现 Habouzit+2021 的"高红移由高效吸积者主导"结构。
- 注意：这是**代理量不是物理量**（caveat 必须写）。

#### 图 P1-2：黑洞质量密度 Ω_BH(z)
- 对 BHMF 积分得 ρ_BH(z)=∫M Φ(M)dM，对标 Sijacki+2015 质量密度演化曲线。
- 判据：z=0 处 ρ_BH 应落在 ~(2–6)×10⁶ M☉/Mpc³ 量级（SMBH 总质量密度经典值）。

#### 图 P1-3：轻种子分布图（S2→S3 的桥）
- 把 P0-4 的遗迹 MF 整理成"轻种子输入格式"（每红移的质量函数+宿主 halo 质量关联），
  写成半解析生长模型的输入说明文档（对接 SHARK/L-Galaxies 式逻辑，
  参考 Rauf+2023 的桥接结构）。

#### 图 P1-4：全天光锥黑洞分布图（4.2）
- 用 1.3 光锥切片 + 4.1 遗迹质量，出 Hammer-Aitoff 全天投影 + 按距离分层统计。
- **这是本项目独有图**（领域内 SAM/模拟都不做遗迹全天分布），可作方法学亮点。

#### 图 P1-5：PISN 质量间隙正式图
- 把 `quantify_pisn_effect.py` 的 none/S15/S17 对比做成正式出版风格图：
  BHMF 差异带 + 间隙位置标注 + GWTC-3/4 观测间隙带（45–60 M☉）叠加。

### P2（数据或模型不全，仅作方向记录）

| 图 | 缺什么 |
|---|---|
| Eddington 比分布函数（ERDF） | 目录无吸积率/光度列（Ding+2025 的标准图，做不了） |
| 类星体光度函数/聚类 | 同上（需光度） |
| 双黑洞并合率与 GW 预言 | P3-OPTIONAL（并合延迟卷积未实现） |
| 聚类/QHMF | 需晕偏置分析，非本期重点 |

---

## 4. Arena 执行包（可直接粘贴的任务 prompt）

> 用法：以下三段可直接发给 Arena coding agent（工作目录 bh-mass-spectrum）。
> 每段都自带验收标准，agent 完成后按 §5 验收。

### 任务 A：多红移 BHMF + 占据率（P0-1、P0-2）
```
任务：在 bh-mass-spectrum 仓库新增 scripts/tng_bhmf_occupancy.py，用 TNG 目录
（/Users/a1-6/tng_dark_trees，注意 agent 环境路径需确认）完成两张图：

1. 多红移 BHMF：z=0/0.5/1/2/4/6（用 header 快照表选 snap），bin 0.25 dex，
   输出 Phi(log M_bh) 单位 h^3 Mpc^-3 dex^-1，质量单位 Msun/h；
2. 黑洞占据率 f_occ(log M_h)：10 档，z=0/1/2/4 四条曲线 + m_bh 阈值扫描版
   （>1e6 与 >1e7 Msun/h 两版）。

硬约束：
- 沿用 scripts/tng_catalog_figures.py 的读取方式（BARYON_FIELD_MAP 显式请求 m_bh/m_h）；
- 图内文字中文（默认；投稿英文期刊时再切英文）；每张图配 summary JSON（数据列/单位/快照/筛选/caveat）；
- caveat 必须包含：重子字段按数据原值使用（来源未经独立确认）、非零值仅
  tree.0–5、低质量端 3387 Msun/h 硬下限尖峰非物理；
- 通过 tests/test_docs_convention.py 的模块 docstring 规范；
- 不动 tng_parser.py 的现有接口；不新增依赖。

验收：图数量级对标 Habouzit+2021 的 TNG100 BHMF（±1 dex）；f_occ 在
m_h≳1e11.5 Msun/h 趋近 1；pytest 全绿。
```

### 任务 B：标度关系演化三联图（P0-3）
```
任务：新增 scripts/tng_scaling_evolution.py，画 MBH–M*、MBH–M_h、MBH–v_max
三联图，z=0/1/2/4 分面（或叠画），散点淡色+中位数趋势+16-84 分位带。
数据列 m_bh/m_s/m_h/v_max（v_max 单位 1e3 km/s）。同样配 summary JSON 与
中文图内文字与 caveat。验收：MBH–M* 的 Spearman 相关 >0.5；v_max 版比 m_h 版
更紧；低质量端趋势变平（与 Habouzit+2021 低端结论一致）。约束同任务 A。
```

### 任务 C：遗迹 MF + PISN 间隙图（P0-4、P1-5）
> 执行细则（数据路径、口径决策、验收判据）与"我们 vs Sicilia+2022 I 创新点对照表"见
> `docs/任务C_遗迹MF与创新点.md`——Arena 派活前必读，该文档所有数字均经代码/数据/原文核实。
```
任务：扩展 scripts/quantify_pisn_effect.py 或新增 scripts/remnant_mf_pisn.py：
用 4.1 推前输出画 z=0/0.5/1/2/4 的恒星 BH 遗迹质量函数，并叠加 none vs S17
的差异带（S15 注明为恒等变换）。物理不变量必须逐位不变：<m>=0.351369、
eta(20)=1.974172e-03、MW Ndot=4.547182e-03。验收：MF 呈"平段+对数正态尾"；
MW 标定量级一致；差异带在低 Z 显形（间隙 58.6-83.0 Msun）。
```

---

## 5. 验收清单（每张图交付前逐项打勾）

- [ ] 口径符合 §2（单位/h/体积/caveat/中文图内文字）；
- [ ] 数量级/形状对标文献（各图"判据"条）；
- [ ] 物理不变量未破坏（涉及 4.1 的图：跑 `tests/` 全绿 + 三个不变量逐位比对）；
- [ ] summary JSON 与图同目录，字段齐全；
- [ ] caveat 文本包含：数据原值使用、tree.0–5 覆盖限制、3387 Msun/h 硬下限；
- [ ] 脚本过 `tests/test_docs_convention.py`；
- [ ] 从仓库根目录跑 pytest（必须仓库根；`zsh scripts/run_tests.sh` 已内置 cd 与 basetemp 规避）。

---

## 6. 与现有资产的映射

| 已有资产 | 在 SOP 中的位置 |
|---|---|
| `scripts/tng_catalog_figures.py` | P0-5（规范化）+ P0-1/2/3 的读取模板 |
| `scripts/quantify_pisn_effect.py` | P0-4 / P1-5 的数值基础 |
| `scripts/field_figures.py` | 示意样本图（A–E），非真实数据，勿当结果 |
| `artifacts/相关工作调研_近十年BH质量谱.md` | 调研依据（证据层） |
| `1_Data_Ingestion_Cosmology/1.2_Simulation_Extractor/notes/TNG数据说明书.md` | 数据口径细节 |
| `artifacts/物理管线逐步讲解.md` | 术语与物理含义速查 |

#### 图 P1-5 产出登记（r190, 2026-11-02）
- **fig4_pisn_gap_vs_gwtc4.png** 已落盘 `artifacts/pisn_experiment/`：
  none/S15/S17 三模型归一化 BHMF（dN/dlogM，per unit SFR）+ GWTC-4.0 观测间隙带（45–60 M☉，金色阴影）。
- 关键读数：S17 在 MW 金属度下 exact-zero 窗口 = 58.6–89.0 M☉（19 bins），与观测间隙带 45–60 M☉
  部分重叠（上沿对齐），但模型缺口比观测更宽且偏高端——caveat：本图为单金属度切片（Z=0.02），
  非全宇宙积分；正式出版版需叠多金属度混合 + 双星通道修正（当前为简化版，与 Sicilia 差异已标注）。
- 数据来源：`pisn_experiment.json`（composite 段）+ `literature/notes/gwtc4-bhmf-numbers.md`（观测侧锚点）。
