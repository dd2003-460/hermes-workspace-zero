# 项目文件夹规范 SPEC（通用复用版）

> 位置：`/Users/a1-6/Desktop/workspace/PROJECT_FOLDER_SPEC.md`
> 用法：新建任何项目时，把本节“发给另一个 agent 的指令”复制粘贴，替换 `{{PROJECT_PATH}}` 和任务树即可。不需要预建实体模版文件夹，示例只看本文档符号树。

## 1. 核心规则

1. **一文件夹 = 一任务节点**。多层结构，编号点分延续：顶层 `1_xxx/、2_xxx/`，子层 `1.1_xxx、1.2_xxx、2.1_xxx…`，可深到 `x.y.z`。
2. **最小单元（叶子，不再分解）下有 `src/` 放代码**。代码需结构化时在 `src/` 下继续建子模块文件夹（如 `src/dataset/`），每个子模块文件夹也要有自己的 `README.md`。
3. **非叶子禁止直接放 `src/` 或代码文件**，只能放子任务文件夹 + `README.md`。
4. 根目录除编号任务外，允许放 `config/、data/` 等全局横切文件夹（见示例），但业务逻辑必须进编号任务。
5. 命名：`<编号>_<英文短名>`，如 `1_Data_Ingestion_Cosmology`、`1.1_Cosmology_Framework`。`src/` 固定小写。

## 2. README 规则（每个文件夹一个，md 格式）

每个文件夹（含根、每级任务、`src/`、代码子模块）必须有一个 `README.md`，固定写三件套：

- **本文件夹主要功能**
- **接口**（输入 / 输出 / 对外函数签名）
- **调用说明**（如何被上层调用、运行命令、依赖）

**作用域铁律**：只描述所在文件夹的功能，不描述分解后子模块的功能。子模块功能只写在子模块自己的 `README.md` 里。父 `README` 如需提子模块，只列编号 + 文件夹名链接，不展开。

## 3. 标准示例（符号树，以 CosmoBH 为例，复用到其他项目时只换任务名）

```
CosmoBH_Project/
├── README.md                      # 项目全局总览与快速启动
├── config/                        # 全局运行配置参数（YAML/JSON）
├── data/                          # 外部数据、中间缓存与输出数据入口
├── 1_Data_Ingestion_Cosmology/    # 一级任务1：宇宙学框架与模拟数据接入
│   ├── README.md                  # 该级功能、接口与使用规范
│   ├── 1.1_Cosmology_Framework/   # 二级任务1.1：标准宇宙学本底计算
│   │   ├── README.md
│   │   └── src/                   # 最小功能单元代码实现
│   └── 1.2_Simulation_Extractor/  # 二级任务1.2：宇宙学模拟原始网格/粒子数据摄取与清洗
│       ├── README.md
│       └── src/
├── 2_Stellar_Mass_BH_Engine/      # 一级任务2：恒星级黑洞形成与遗迹质量引擎
│   ├── README.md                  # 该级功能、接口与使用规范
│   ├── 2.1_Remnant_Mass_Recipes/  # 二级任务2.1：前身星演化与遗迹质量函数（Spera et al. 2015）
│   │   ├── README.md
│   │   └── src/
│   └── 2.2_Binary_Delay_Kicks/    # 二级任务2.2：双星并合时间延迟与超新星踢速度（Dominik et al. 2013）
│       ├── README.md
│       └── src/
├── 3_Massive_BH_Growth_Engine/    # 一级任务3：中等与超大质量黑洞（IMBH/SMBH）演化
│   ├── README.md                  # 该级功能、接口与使用规范
│   ├── 3.1_Seed_Generation/       # 二级任务3.1：早期宇宙黑洞种子植入模型
│   │   ├── README.md
│   │   └── src/
│   └── 3.2_Accretion_Merger/      # 二级任务3.2：宇宙学尺度吸积与动力学并合生长
│       ├── README.md
│       └── src/
├── 4_Population_Synthesis/        # 一级任务4：全宇宙黑洞种群宇宙学卷积
│   ├── README.md                  # 该级功能、接口与使用规范
│   ├── 4.1_Convolution_Engine/    # 二级任务4.1：SFR、金属丰度演化与积分管道
│   │   ├── README.md
│   │   └── src/
│   └── 4.2_Spatial_Mock_Catalog/  # 二级任务4.2：光锥投影与空间三维模拟巡天表生成
│       ├── README.md
│       └── src/
└── 5_Statistical_Analysis/        # 一级任务5：统计预测、质量谱构建与可视化
    ├── README.md                  # 该级功能、接口与使用规范
    ├── 5.1_Mass_Functions/        # 二级任务5.1：全局全质量黑洞质量函数与红移演化分析
    │   ├── README.md
    │   └── src/
    └── 5.2_Observational_Plots/   # 二级任务5.2：观测对比图表与数据发布接口
        ├── README.md
        └── src/
```

`src/` 下需结构化时示例：

```
1.1_Cosmology_Framework/src/
├── README.md          # 本叶子代码入口、接口与运行命令，不展开子模块算法
├── cosmology/         # 子模块：各有自己的 README.md（功能+接口+调用）
│   └── README.md
└── utils/
    └── README.md
```

## 4. 发给另一个 agent 的指令（直接复制）

> 在 `{{PROJECT_PATH}}` 下按本文档建文件夹结构。任务树以指令中给出的树为准，形状参照第3节示例。
> 要求：(1) 每层文件夹对应一级任务分解，编号如 `1/1.1/1.2、2/2.1`；(2) 最小单元下建 `src/` 放代码，`src/` 下可再建子模块文件夹；(3) 每个文件夹写 `README.md`（功能+接口+调用说明），只讲本层，不讲子模块，子模块功能在子模块 README 里。
> 建完输出 `find` 列表自检：叶子都有 `src/`、非叶子都没有、每个文件夹都有 `README.md`。
